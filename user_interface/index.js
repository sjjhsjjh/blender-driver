class Main {
    createNode(tag, text) {
        var element = document.createElement(tag);
        if ( text !== null ) {
            element.appendChild( document.createTextNode(text) );
        }
        return element;
    }
    
    appendNode(tag, text, parent) {
        return parent.appendChild( this.createNode(tag, text) );
    }

    constructor(userInterfaceID) {
        this.userInterface = document.getElementById(userInterfaceID);
    }
    
    main() {
        
        fetch('api/root/camera')
        .then(response => response.json())
        .then(response => {
            console.log(response);
            this.appendNode('pre',
                            JSON.stringify(response, null, "  "),
                            this.userInterface);
        });
    }
}

function main(userInterfaceID) {
    let mainMain = new Main(userInterfaceID);
    return mainMain.main();
}