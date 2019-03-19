import { Component, h } from "preact";
import { API_ROOT, System } from "./models";
import MemberCard from "./MemberCard";

interface Props {
    id: string
}

interface State {
    system: System
}

export default class SystemPage extends Component<Props, State> {
    componentDidMount() {
        this.fetchData();
    }

    async fetchData() {
        const data = await fetch(API_ROOT + "/s/" + this.props.id);
        const json = await data.json();
        const member_data = await fetch(API_ROOT + "/s/" + this.props.id + "/members"); //the members was split into another page
        json.members = await member_data.json(); //this is so the rest can stay as it is
        this.setState({system: json, ...this.state});
    }

    render() {
        if (this.state.system) {
            return (<div>
                { this.state.system.members.map(m => (<MemberCard member={m} />)) }
            </div>)
        }
        return (<div></div>);
    }
}
