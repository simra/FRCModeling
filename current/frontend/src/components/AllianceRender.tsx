import React, { useState, useEffect } from "react";
import { Alliance } from "../types/Alliance";
import { Team } from "../types/TeamTypes";
import { Droppable, Draggable, DragDropContext, DroppableProvided, DraggableProvided, DroppableProps } from "react-beautiful-dnd";
import StrictModeDroppable from "./StrictModeDroppable";


interface AllianceProps {
    alliance: Alliance;
}

function AllianceRender({alliance}: AllianceProps) {
    return (
        <div className="alliance-render">
            <div>A{alliance.id}</div>
            {
                // here we want to insert three droppable target divs for the teams in the alliance
                alliance.teams.map((team, index) => {
                    return (
                        <StrictModeDroppable droppableId={"alliance" + alliance.id + "-team" + index}>
                            {(provided: DroppableProvided) => (
                                <div ref={provided.innerRef} {...provided.droppableProps} className="alliance-team">
                                    {team.number+' '+team.nickname}
                                    {provided.placeholder}
                                </div>
                            )}
                        </StrictModeDroppable>
                    );
                }
                )
            }
            <div>{alliance.winProbability || ''}</div>
        </div>
    );
}

export default AllianceRender;