import React, { Component, Fragment } from "react";
// import logo from './logo.svg';
import './App.css';
import Header from './MainHeader';
import Footer from './MainFooter';
import { layoutStyles } from './layout_styles.js';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      display: "login",
      username: "Anonymous",
      gameBalance: 0,
      allTimeBalance: 0,
      smallBlind: 0,
      activePlayers: {}, // player i uses cards i and i + 1, objects like 0:{...info}
      leaderboardState: {}, // to show for all time, each entry like 'Aayush':3.45
      faceUpHandCards: {},
      faceUpHoleCards: [] 
    };
    this._updateBalance = newBalance => {
      //write to firebase @ michael
      this.setState({ gameBalance: newBalance });
    };

    this._updateGameState = newActivePlayers => { //write to firebase @ michael
      this.setState({ activePlayers: newActivePlayers });
    };

    this._updateLeaderboardState = newLeaderboardState => { //write to firebase @ michael
      this.setState({ leaderboardState: newLeaderboardState });
    };

    this._getNewGameInfo = userName => {
      // fetch active players 
      // fetch current cards
      // called on login
    };
  }
  
  async login(){
    this.setState({activePlayers: {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}, 7:{}, 8:{}}}); //
    this.setState({faceUpHandCards: {
      // 0: '2C',
      // 1: '2S'
    }});
    this.setState({faceUpHoleCards: {
    }});
    this.setState({display: "game"})
  }
  
  async componentDidMount() {
    console.log("Mounting App.js");
    // EXAMPLE NODE CALL
    // var res = await fetch(`/get_username`);
    // res = await res.json();
    // console.log(`Unique id: ${res["id"]}.`);

    // TODO: REPLACE WITH ACTUAL ENDPOINTS
    // CURRENTLY POPULATED WITH RANDOM EXAMPLE SHIT, 
    // THIS STUFF NEEDS TO BE SET NOT IN DIDMOUNT BUT ON SOME METHOD CALLED POSTLOGIN
    this.login();
  }

  render() {
    if (this.state.display === "initial") return <h1>Loading...</h1>; 
    if(this.state.display === "login"){
        // loginOverlay = (<LoginOverlay><</LoginOverlay>) // adam to fill out
    }
    console.log("rendering app.js with state", this.state);
    console.log(layoutStyles)
    return (
      <Fragment>
        <div style={layoutStyles.header}>
          <Header/>
        </div>
        <div style={layoutStyles.footer}>
          <Footer/>
        </div>
      </Fragment>
    );
	}
}
export const LeaderboardWidthPercent = 15;
export default App;
