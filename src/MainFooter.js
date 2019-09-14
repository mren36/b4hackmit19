import React, {Fragment} from "react";
import styled, {css} from "styled-components"

class Footer extends React.Component  {
    constructor(props) {
      super(props);
      this.state = {}
    };
    render() {
        return(
            <Fragment>
                <RedFooter/>
                <SongTextField defaultValue="https://www.youtube.com/watch?v=XMqEFuGA2cE" />
                <GetLinkButton> Go </GetLinkButton>
            </Fragment>
        );
    }
}

const RedFooter = styled.div`
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
    border-radius: 0px 10px 10px 0px;
`;

const GetLinkButton = styled(Button)`
    left: 60%;
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

const SongTextField = styled.input`
    position: absolute;
    font-family: Rambla;
    right: 50%;
    font-size: 0.9em;
    text-align: center;
    vertical-align: middle;
    width: 40%;
    left: 20%;
    height: 70%;
    top: 15%;
    placeholder: "Youtube URL";

    border: 1px solid black;
    box-sizing: border-box;
    border-radius: 10px 0px 0px 10px;
`;

export default Footer;