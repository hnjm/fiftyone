import styled from "styled-components";

export const ActionItem = styled.div`
  display: flex;
  align-content: center;
  text-align: center;
  cursor: pointer;
  color: var(--joy-palette-text-secondary);
  -webkit-transition: 0.2s ease-in-out;
  -moz-transition: 0.2s ease-in-out;
  -o-transition: 0.2s ease-in-out;
  transition: 0.2s ease-in-out;

  &:hover {
    transform: translate(0, -1px);
  }
`;

export const ActionBarContainer = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  opacity: 1;
  z-index: 20;
  justify-items: center;
  align-items: center;
  display: flex;

  color: #eee;

  -webkit-transition: opacity 0.5s;
  -moz-transition: opacity 0.5s;
  -o-transition: opacity 0.5s;
  -ms-transition: opacity 0.5s;
  transition: opacity 0.5s;
  width: 100%;

  opacity: 0.95;
  height: 37px;
  background-color: var(--joy-palette-background-level3);
  border: 1px solid var(--joy-palette-primary-plainBorder);
  border-left: 0;
  padding: 0 1rem;
`;

export const ActionsBar = styled.div`
  position: relative;
  display: flex;
  flex-grow: 1;
  justify-content: end;
  row-gap: 0.5rem;
  column-gap: 0.75rem;
  align-items: center;
  height: 2.3rem;
`;

export const ActionPopOverDiv = styled.div`
  width: 16rem;
  position: absolute;
  bottom: 2.5rem;
  background-color: var(--joy-palette-background-level2);
  border: 1px solid var(--joy-palette-primary-plainBorder);
  box-shadow: 0 8px 15px 0 var(--joy-palette-neutral-softBg);
  border-radius: 3px;
  color: var(--joy-palette-text-secondary);
  overflow: hidden;
`;

export const ActionPopOverInner = styled.div`
  padding: 0 0.25rem;
`;

export const Container = styled.div`
  height: 100%;
  width: 100%;
  position: relative;
`;

export const ViewButton = styled.div`
  line-height: 1rem;
  padding: 3px 6px;
  background-color: var(--joy-palette-text-secondary);
  color: var(--joy-palette-text-invert);
  border-radius: 1rem;
  border: none;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  opacity: 1;
`;
