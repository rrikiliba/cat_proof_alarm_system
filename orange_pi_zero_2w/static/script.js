var client;
var isArmed = false;

const hostname = window.location.hostname;

function onConnect() {
    client.subscribe('device/ack/webapp')
    client.subscribe('image/submit')
    client.subscribe('alarm/disarm')
    client.subscribe('alarm/sound')
    client.subscribe('alarm/rearm')
    console.log("Connected to broker");
    document.getElementById('brokerStatus').textContent = "Broker status: Connected";
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("Connection lost: " + responseObject.errorMessage);
    }
    document.getElementById('setAlarm').disabled = true;
    // Mostra un pop-up di errore
    alert("Connection lost!");
}

function onMessageArrived(message) {
    console.log("Message arrived: " + message.payloadString);
    if (message.destinationName === "alarm/disarm") {
        console.log("Alarm state: " + message.payloadString);
        isArmed = false;
        setButtonState();
    }
    else if(message.destinationName === "image/submit") {
        const image = document.createElement('image');
        const bytes = new Blob(message.payloadBytes);
        image.src = URL.createObjectURL(bytes);
        document.getElementById('imageConteiner').appendChild(image);
        onImageRecived();
    }
    else if(message.destinationName === "alarm/rearm") {
        document.getElementById('setAlarm').disabled = false;
        isArmed = true;
        setButtonState();
    }
    else if(message.destinationName === "device/ack/webapp") {
        if (message.payloadString === '0') {
            isArmed = false;
        } else {
            isArmed = true;
        }
        setButtonState();
    }
}

function setButtonState() {
    if (isArmed) {
        document.getElementById('setAlarm').textContent = "Disarm";
    }else {
        document.getElementById('setAlarm').textContent = "Arm";
    }
    console.log("IsArmed: " + isArmed);
}

function onImageRecived(){
    console.log("Image received");
    document.getElementById('callTheCops').style.display = 'block';
}

document.getElementById('brokerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    var brokerPassword = document.getElementById('brokerPassword').value;

    try {
        client = new Paho.MQTT.Client(hostname, Number(9001), "webapp");
        client.onConnectionLost = onConnectionLost;
        client.onMessageArrived = onMessageArrived;
        client.connect({
            onSuccess: onConnect,
            onFailure: function (error) {
                console.log("Connection failed: ", error.errorMessage);
            },
            userName: "admin",
            password: brokerPassword
        });
    } catch (error) {
        console.error("Failed to connect to broker: ", error);
        alert("Failed to connect to broker: " + error.message);
    }
});

document.getElementById('arm').addEventListener('click', function() {
    if(!isArmed) {
        if (client && client.isConnected()) {
            var message = new Paho.MQTT.Message("armed");
            message.destinationName = "alarm/rearm";
            client.send(message);
            console.log("Message sent: armed");
            isArmed = true;
        } else {
            console.log("Client is not connected");
            alert("Broker is not connected");
        }
    }else{
        if (client && client.isConnected()) {
            var message = new Paho.MQTT.Message("disarmed");
            message.destinationName = "alarm/disarm";
            client.send(message);
            console.log("Message sent: disarmed");
            isArmed = false;
        } else {
            console.log("Client is not connected");
            alert("Broker is not connected");
        }
    }
    setButtonState();
});