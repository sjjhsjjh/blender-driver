class UserInterface {
    createNode(tag, text) {
        var element = document.createElement(tag);
        if ( text !== null ) {
            element.appendChild(document.createTextNode(text));
        }
        return element;
    }
    
    appendNode(tag, text, parent) {
        return parent.appendChild(this.createNode(tag, text));
    }

    constructor(userInterfaceID) {
        this.userInterface = document.getElementById(userInterfaceID);
    }
    
    fetch_api(...path) {
        return fetch(['api', ...path].join('/'));
    }
    
    fetch_camera() {
        this.fetch_api('root', 'camera')
        .then(response => response.json())
        .then(response => {
            console.log('camera', response);
            this.appendNode('pre',
                            JSON.stringify(response, null, "  "),
                            this.userInterface);
            if (response.subjectPath) {
                this.fetch_api(...response.subjectPath)
                .then(response2 => response2.json())
                .then(response2 => {
                    console.log('subject', response2);
                });
            }
        });
    }
    
    show() {
        this.button = this.appendNode('button', "Fetch camera", this.userInterface);
        this.button.setAttribute('type', 'button');
        this.button.onclick = this.fetch_camera.bind(this);
        
        return this;
    }
}

function main(userInterfaceID) {
    const userInterface = new UserInterface(userInterfaceID);
    return userInterface.show();
}