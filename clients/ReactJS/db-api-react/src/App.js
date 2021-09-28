
/* src/App.js
 *
 * React application using the fetch API to send a GET request to consume JSON data from a third-party REST API in the componendDidMount() life-cycle method.
 * uses the state object to hold the fetched JSON data and the setState() method to set the state.
 *
 */

import React, { Component } from 'react';

const url = 'http://127.0.0.1:8980/api';
const base64 = '';

class App extends Component {

  state = {
    items: []
  }

  componentDidMount() {

    fetch(url, { headers:{ Authorization: 'Basic ' + base64 } })
    .then(res => res.json())
    .then((data) => {
      this.setState({ items: data })
      console.log(this.state.items)
    })
    .catch(console.log)
  }

  render() {

    return (
       <div className="container">
        <h1>Show Databases</h1>

        {this.state.items.map((item) => (
              <li className="">{item}</li>
        ))}

       </div>
    );
  }

}

export default App;

