import { Member } from "./models";
import { h } from "preact";

export default (p: {member: Member}) => (
    <div class="member-card">
        <div class="header">
            <span class="name">{ p.member.name }</span>
        </div>

        <p class="description">{ p.member.description }</p>
    </div>
);