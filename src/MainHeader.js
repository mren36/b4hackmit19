import React, {Fragment} from "react";
import styled, {css} from "styled-components"

class Header extends React.Component  {
    constructor(props) {
      super(props);
      this.state = {}
    };
    render() {
        return(
            <Fragment>
                <RedHeader/>
                <Text> Singerator </Text>
                <NewGameButton> Start </NewGameButton>
                <CopyLinkButton> New Song </CopyLinkButton>
            </Fragment>
        );
    }
}

const RedHeader = styled.div`
    position: absolute;
    width:100%;
    height:100%;
    background: #D02000;
    z-index: -1;

`;

const Button = styled.button`
    font-size: 0.9em;
    font-face: Gill Sans;
    color: white;
    font-weight: bold;
    border: 1px solid white;

    position: absolute;
    width: 10%;
    height: 70%;
    top: 15%;

    background: #D02000;
    border-radius: 10px;
`;

const CopyLinkButton = styled(Button)`
    left: 51%;
`;

const NewGameButton = styled(Button)`
    left: 39%;
`;

export const Text = styled.span`
    font-size: 0.9em;
    font-face: Gill Sans;
    color: white;
    font-weight: bold;

    position: absolute;
    width: 10%;
    top: 30%;
    left: 2%;
    text-align: center;
    vertical-align: middle;

    background: #D02000;
    border-radius: 10px;
`
export default Header;