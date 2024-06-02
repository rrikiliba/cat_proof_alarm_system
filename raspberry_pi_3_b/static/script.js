var client;
var isArmed = false;

function onConnect() {
    console.log("Connected to broker");
    document.getElementById('brokerStatus').textContent = "Broker status: Connected";
    client.subscribe('image/request')
    client.subscribe('device/online')
    client.subscribe('device/offline')
    client.subscribe('alarm/disarm')
    client.subscribe('alarm/defuse')
    client.subscribe('alarm/rearm')

    isArmed = true;
    setButtonState();
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
    if(message.destinationName === "image/submit") {
        document.getElementById('image').src = "data:image/jpeg;base64," + message.payloadString;
        onImageRecived();
    }
    if(message.destinationName === "device/online") {
        document.getElementById('setAlarm').disabled = false;
        document.getElementById('alarmStatus').textContent = "Broker status: Connected";
    }
    if(message.destinationName === "device/offline") {
        document.getElementById('setAlarm').disabled = true;
        document.getElementById('alarmStatus').textContent = "Alarm status: Disconnected";
    }
    if(message.destinationName === "alarm/defuse") {
        document.getElementById('setAlarm').disabled = false;
        isArmed = false;
        setButtonState();
    }
    if(message.destinationName === "alarm/rearm") {
        document.getElementById('setAlarm').disabled = false;
        isArmed = true;
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
    var brokerAddress = document.getElementById('brokerAddress').value;

    client = new Paho.MQTT.Client(brokerAddress, Number(9001), "clientId");
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    client.connect({
        onSuccess: onConnect,
        onFailure: function (error) {
            console.log("Connection failed: ", error.errorMessage);
        },
    });
});

document.getElementById('setAlarm').addEventListener('click', function() {
    if(!isArmed) {
        if (client && client.isConnected()) {
            var message = new Paho.MQTT.Message("armed");
            message.destinationName = "alarm/arm";
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