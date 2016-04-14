import React from 'react';
import TextField  from 'material-ui/lib/text-field';

export default class ChoiceItem extends React.Component {
  constructor(props){
    super(props);
    this.errors = {};
  }

  onChange(event){

  }

  render(){
      return (
        <div>
          <TextField
            errorText={this.errors.name}
            onChange={this.onChange}
            value={this.props.choiceItem.name}
            name="name"
            multiLine={true}
          />

          <TextField
            errorText={this.errors.label}
            onChange={this.onChange}
            value={this.props.choiceItem.label}
            name="label"
            multiLine={true}
          />
        </div>

      );
  }
}
