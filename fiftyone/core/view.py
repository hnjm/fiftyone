"""
Core definitions of FiftyOne dataset views.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
# pragma pylint: disable=redefined-builtin
# pragma pylint: disable=unused-wildcard-import
# pragma pylint: disable=wildcard-import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import *

# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import

from copy import copy, deepcopy

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

import fiftyone.core.collections as foc
import fiftyone.core.odm as foo
import fiftyone.core.sample as fos


class DatasetView(foc.SampleCollection):
    """A view into a :class:`fiftyone.core.dataset.Dataset`.

    Dataset views represent read-only collections of
    :class:`fiftyone.core.sample.Sample` instances in a dataset.

    Operations on dataset views are designed to be chained together to yield
    the desired subset of the dataset, which is then iterated over to directly
    access the samples.

    Example use::

        # Print the paths to 5 random data samples in the dataset
        view =
            .sort_by("metadata.size_bytes")
            .take(5)
        )
        for sample in dataset.default_view().take(5, random=True):
            print(sample.filepath)

    Args:
        dataset: a :class:`fiftyone.core.dataset.Dataset`
    """

    def __init__(self, dataset):
        self._dataset = dataset
        self._pipeline = []

    @property
    def _sample_cls(self):
        return self._dataset._sample_cls

    def __len__(self):
        result = self.aggregate(self._pipeline + [{"$count": "count"}])
        return next(result)["count"]

    def __getitem__(self, sample_id):
        # try to find the sample_id in the pipeline
        try:
            pipeline = [{"$match": {"_id": ObjectId(sample_id)}}]
            next(self.aggregate(pipeline))
            found = True
        except StopIteration:
            found = False

        # sample_id not in pipeline
        if not found:
            raise KeyError("No sample found with ID '%s'" % sample_id)

        return self._dataset[sample_id]

    def __copy__(self):
        view = self.__class__(self._dataset)
        view._pipeline = deepcopy(self._pipeline)
        return view

    def summary(self):
        """Returns a string summary of the view.

        Returns:
            a string summary
        """
        pipeline_str = "\t" + "\n\t".join(
            [
                "%d. %s" % (idx, str(d))
                for idx, d in enumerate(self._pipeline, start=1)
            ]
        )

        return "\n".join(
            [
                "Num samples:    %d" % len(self),
                "Tags:           %s" % self.get_tags(),
                "Label groups:   %s" % self.get_label_groups(),
                "Insight groups: %s" % self.get_insight_groups(),
                "Pipeline stages:\n%s" % pipeline_str,
            ]
        )

    def get_tags(self):
        """Returns the list of tags in the collection.

        Returns:
            a list of tags
        """
        pipeline = [
            {"$project": {"tags": "$tags"}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "None", "all_tags": {"$addToSet": "$tags"}}},
        ]
        try:
            return next(self.aggregate(pipeline))["all_tags"]
        except StopIteration:
            pass
        return []

    def iter_samples(self):
        """Returns an iterator over the samples in the view.

        Returns:
            an iterator over :class:`fiftyone.core.sample.Sample` instances
        """
        for d in self.aggregate():
            yield self._deserialize_sample(d)

    def aggregate(self, pipeline=None):
        """Calls a MongoDB aggregation pipeline on the view

        Args:
            pipeline (None): an optional aggregation pipeline (list of dicts)
                to append to the view's pipeline before aggregation.

        Returns:
            an iterable over the aggregation result
        """
        if pipeline is None:
            pipeline = []

        return self._get_ds_qs().aggregate(self._pipeline + pipeline)

    def iter_samples_with_index(self):
        """Returns an iterator over the samples in the view together with
        their integer index in the collection.

        Returns:
            an iterator that emits ``(index, sample)`` tuples, where:

                - ``index`` is an integer index relative to the offset, where
                  ``offset <= view_idx < offset + limit``

                - ``sample`` is a :class:`fiftyone.core.sample.Sample`
        """
        offset = self._get_latest_offset()
        iterator = self.iter_samples()
        for idx, sample in enumerate(iterator, start=offset):
            yield idx, sample

    def filter(
        self, tag=None, insight_group=None, label_group=None, filter=None
    ):
        """Filters the samples in the view by the given filter.

        Args:
            tag (None): a sample tag string
            insight_group (None): an insight group string
            label_group (None): a label group string
            filter (None): a MongoDB query dict. See
                https://docs.mongodb.com/manual/tutorial/query-documents
                for details

        Returns:
            a :class:`DatasetView`
        """
        view = self

        if tag is not None:
            view = view._copy_with_new_stage({"$match": {"tags": tag}})

        if insight_group is not None:
            # @todo(Tyler) should this filter the insights as well? or just
            # filter the samples based on whether or not the insight is
            # present?
            raise NotImplementedError("Not yet implemented")

        if label_group is not None:
            # @todo(Tyler) should this filter the labels as well? or just
            # filter the samples based on whether or not the label is
            # present?
            raise NotImplementedError("Not yet implemented")

        if filter is not None:
            view = view._copy_with_new_stage({"$match": filter})

        return view

    def sort_by(self, field, reverse=False):
        """Sorts the samples in the view by the given field.

        Args:
            field: the field to sort by. Example fields::

                filename
                metadata.size_bytes
                metadata.frame_size[0]

            reverse (False): whether to return the results in descending order

        Returns:
            a :class:`DatasetView`
        """
        order = DESCENDING if reverse else ASCENDING
        return self._copy_with_new_stage({"$sort": {field: order}})

    def take(self, size, random=False):
        """Takes the given number of samples from the view.

        Args:
            size: the number of samples to return
            random (False): whether to randomly select the samples

        Returns:
            a :class:`DatasetView`
        """
        if random:
            stage = {"$sample": {"size": size}}
        else:
            stage = {"$limit": size}

        return self._copy_with_new_stage(stage)

    def offset(self, offset):
        """Omits the given number of samples from the head of the view.

        Args:
            offset: the offset

        Returns:
            a :class:`DatasetView`
        """
        return self._copy_with_new_stage({"$skip": offset})

    def select(self, sample_ids):
        """Selects only the samples with the given IDs from the view.

        Args:
            sample_ids: an iterable of sample IDs

        Returns:
            a :class:`DatasetView`
        """
        sample_ids = [ObjectId(id) for id in sample_ids]
        return self._copy_with_new_stage(
            {"$match": {"_id": {"$in": sample_ids}}}
        )

    def exclude(self, sample_ids):
        """Excludes the samples with the given IDs from the view.

        Args:
            sample_ids: an iterable of sample IDs

        Returns:
            a :class:`DatasetView`
        """
        sample_ids = [ObjectId(id) for id in sample_ids]
        return self._copy_with_new_stage(
            {"$match": {"_id": {"$not": {"$in": sample_ids}}}}
        )

    def _get_ds_qs(self, **kwargs):
        return self._dataset._get_query_set(**kwargs)

    @staticmethod
    def _deserialize_sample(d):
        return fos.Sample.from_doc(
            foo.ODMSample.from_dict(d, created=False, extended=False)
        )

    def _copy_with_new_stage(self, stage):
        view = copy(self)
        view._pipeline.append(stage)
        return view

    def _get_latest_offset(self):
        """Returns the offset of the last $skip stage."""
        for stage in self._pipeline[::-1]:
            if "$skip" in stage:
                return stage["$skip"]
        return 0