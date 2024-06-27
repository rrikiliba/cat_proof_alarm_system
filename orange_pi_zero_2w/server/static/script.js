var client;
var isArmed = false;

function onConnect() {
    client.subscribe('device/ack/webapp')
    client.subscribe('image/submit')
    client.subscribe('alarm/disarm')
    client.subscribe('alarm/sound')
    client.subscribe('alarm/rearm')
    console.log("Connected to broker");
    updateStatus('brokerStatus', true);
    var message = new Paho.MQTT.Message("webapp");
    message.destinationName = "device/online";
    client.send(message);
    console.log("Message sent: webapp");
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("Connection lost: " + responseObject.errorMessage);
    }
    updateStatus('brokerStatus', false);
    alert("Connection lost!");
}

function onMessageArrived(message) {
    console.log("Message arrived: " + message.payloadString);
    if (message.destinationName === "alarm/disarm") {
        console.log("Alarm state: " + message.payloadString);
        isArmed = false;
        updateStatus('alarmStatus', false);
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
        updateStatus('alarmStatus', true);
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
        client = new Paho.MQTT.Client(window.location.hostname, Number(9001), "webapp");
        client.onConnectionLost = function(responseObject) {
            console.log("Connection lost: ", responseObject.errorMessage);
        };
        client.onMessageArrived = function(message) {
            console.log("Message arrived: ", message.payloadString);
        };
        client.connect({
            onSuccess: function() {
                onConnect();
                console.log("Connected successfully");
            },
            onFailure: function (error) {
                console.log("Connection failed: ", error.errorMessage);
            },
            userName: "admin",
            password: brokerPassword,
            keepAliveInterval: 300
        });
    } catch (error) {
        console.error("Failed to connect to broker: ", error);
        alert("Failed to connect to broker: " + error.message);
    }
});

document.getElementById('togglePassword').addEventListener('click', function() {
    var passwordField = document.getElementById('brokerPassword');
    var passwordFieldType = passwordField.getAttribute('type');
    if (passwordFieldType === 'password') {
        passwordField.setAttribute('type', 'text');
    } else {
        passwordField.setAttribute('type', 'password');
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
            setButtonState();
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
            setButtonState();
        } else {
            console.log("Client is not connected");
            alert("Broker is not connected");
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    updateStatus('brokerStatus', false);
    updateStatus('alarmStatus', false);
});

function updateStatus(elementId, isConnected) {
    const element = document.getElementById(elementId);
    const passwordMessage = document.querySelector('.instruction');
    if (isConnected) {
        element.classList.add('connected');
        element.classList.remove('disconnected');
        element.textContent = `${elementId.replace('Status', ' status')}: Connected`;
        document.getElementById('brokerForm').style.display = 'none';
        document.getElementById('arm').style.display = 'block';
        document.getElementById('systemStatus').style.display = 'block';
        passwordMessage.style.display = 'none';
    } else {
        element.classList.add('disconnected');
        element.classList.remove('connected');
        element.textContent = `${elementId.replace('Status', ' status')}: Disconnected`;

        document.getElementById('brokerForm').style.display = 'block';
        document.getElementById('arm').style.display = 'none';
        document.getElementById('systemStatus').style.display = 'none';
        passwordMessage.style.display = 'block';
    }
    checkSystemStatus();
}

function checkSystemStatus() {
    const brokerConnected = document.getElementById('brokerStatus').classList.contains('connected');
    const alarmConnected = document.getElementById('alarmStatus').classList.contains('connected');
    const systemStatus = document.getElementById('systemStatus');
    const alarmArmed = document.getElementById('alarmArmed');

    if (brokerConnected && alarmConnected) {
        systemStatus.textContent = "The alarm is on";
        systemStatus.classList.add('status-box', 'connected');
        document.getElementById('brokerStatus').style.display = 'none';
        document.getElementById('alarmStatus').style.display = 'none';
    } else {
        systemStatus.textContent = "";
        systemStatus.classList.remove('connected');
    }
    if(isArmed){
        alarmArmed.textContent = "The alarm is armed";
        alarmArmed.classList.add('status-box', 'connected');
    }
    else{
        alarmArmed.textContent = "The alarm is disarmed";
        alarmArmed.classList.add('status-box', 'disconnected');
    }
}