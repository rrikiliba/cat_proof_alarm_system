var client;
var isArmed = false;

const onConnect = () => {
    client.subscribe('device/ack/webapp')
    client.subscribe('image/submit')
    client.subscribe('alarm/disarm')
    client.subscribe('alarm/sound')
    client.subscribe('alarm/rearm')
    updateStatus('brokerStatus', true);
    var message = new Paho.MQTT.Message('webapp');
    message.destinationName = 'device/online';
    client.send(message);
}

const onConnectionLost = (e) => {
    updateStatus('brokerStatus', false);
    updateStatus('alarmStatus', false);
    alert('Connection lost!\n' + e.errorMessage);
}

const onMessageArrived = (message) => {
    if (message.destinationName === 'alarm/disarm') {
        isArmed = false;
        setButtonState();
    }
    else if (message.destinationName === 'image/submit') {
        const arrayBufferView = new Uint8Array(message.payloadBytes);
        const blob = new Blob( [ arrayBufferView ], { type: "image/jpeg" } );
        const imageUrl = URL.createObjectURL(blob);
        const image = new Image(320, 240);
        image.src = imageUrl;
        image.addEventListener('click', () => {
            window.open(imageUrl).focus();
        });
        document.getElementById('imageContainer').appendChild(image);
        onImageRecived();
    }
    else if (message.destinationName === 'alarm/rearm') {
        document.getElementById('arm').disabled = false;
        isArmed = true;
        setButtonState();
    }
    else if (message.destinationName === 'device/ack/webapp') {
        updateStatus('alarmStatus', true);
        if (message.payloadString === '1') {
            isArmed = true;
        } else {
            isArmed = false;
        }
        setButtonState();
    }
}

const onImageRecived = () => {
    document.getElementById('callTheCops').style.display = 'block';
}

document.getElementById('brokerForm').addEventListener('submit', (e) => {
    e.preventDefault();
    var brokerPassword = document.getElementById('brokerPassword').value;
    try {
        client = new Paho.MQTT.Client(window.location.hostname, Number(9001), 'webapp');
        client.connect({
            onSuccess: onConnect,
            onFailure: (error) => {
                alert('Connection failed: ' + error.errorMessage);
                console.log('Connection failed: ', error.errorMessage);
            },
            userName: 'admin',
            password: brokerPassword,
            keepAliveInterval: 0
        });
        client.onConnectionLost = (responseObject) => {
            onConnectionLost(responseObject);
        };
        client.onMessageArrived = onMessageArrived;
    } catch (error) {
        console.error('Failed to connect to broker: ', error);
        alert('Failed to connect to broker: ' + error.message);
    }
});

document.getElementById('togglePassword').addEventListener('click', () => {
    var passwordField = document.getElementById('brokerPassword');
    var passwordFieldType = passwordField.getAttribute('type');
    if (passwordFieldType === 'password') {
        passwordField.setAttribute('type', 'text');
    } else {
        passwordField.setAttribute('type', 'password');
    }
});

document.getElementById('arm').addEventListener('click', () => {
    if (!isArmed) {
        if (client && client.isConnected()) {
            var message = new Paho.MQTT.Message('armed');
            message.destinationName = 'alarm/rearm';
            client.send(message);
            isArmed = true;
            setButtonState();
        } else {
            alert('Broker is not connected');
        }
    } else {
        if (client && client.isConnected()) {
            var message = new Paho.MQTT.Message('disarmed');
            message.destinationName = 'alarm/disarm';
            client.send(message);
            isArmed = false;
            setButtonState();
        } else {
            alert('Broker is not connected');
        }
    }
});

document.getElementById('callTheCops').addEventListener('click', () => {
    window.alert('Just kidding, we can\'t do that');
});

document.addEventListener('DOMContentLoaded', () => {
    updateStatus('brokerStatus', false);
    updateStatus('alarmStatus', false);
});

const updateStatus = (elementId, isConnected) => {
    const element = document.getElementById(elementId);
    const passwordMessage = document.querySelector('.instruction');
    if (isConnected) {
        element.classList.add('connected');
        element.classList.remove('disconnected');
        element.textContent = `${elementId.replace('Status', ' status')}: Connected`;
        document.getElementById('brokerForm').style.display = 'none';
        document.getElementById('brokerStatus').style.display = 'none';
        document.getElementById('systemStatus').style.display = 'block';
        passwordMessage.style.display = 'none';
    } else {
        element.classList.add('disconnected');
        element.classList.remove('connected');
        element.textContent = `${elementId.replace('Status', ' status')}: Disconnected`;
        document.getElementById('brokerForm').style.display = 'block';
        document.getElementById('arm').style.display = 'none';
        document.getElementById('systemStatus').style.display = 'none';
        document.getElementById('brokerForm').style.display = 'block';
        document.getElementById('brokerStatus').style.display = 'block';
        document.getElementById('alarmStatus').style.display = 'block';
        passwordMessage.style.display = 'block';
    }
    checkSystemStatus();
}

const isAlarmConnected = (elementId, isConnected) => {
    const message = document.querySelector('.instruction');
    if (elementId === 'alarmStatus' && !isConnected) {
        document.getElementById('brokerForm').style.display = 'none';
        document.getElementById('brokerStatus').style.display = 'block';
        document.getElementById('systemStatus').style.display = 'block';
        document.getElementById('alarmStatus').style.display = 'block';
        message.textContent = 'Wait for the alarm to connect to the broker';
        message.style.display = 'block';
    }
    else {
        updateStatus(elementId, isConnected);
    }
}

const setButtonState = () => {
    const arm = document.getElementById('arm');
    const alarmArmed = document.getElementById('alarmArmed');
    const message = document.querySelector('.instruction');
    if (isArmed) {
        arm.textContent = 'Disarm';
        alarmArmed.textContent = 'The alarm is armed';
        alarmArmed.classList.remove('disconnected');
        alarmArmed.classList.add('connected');
        message.style.display = 'none';
    } else {
        arm.textContent = 'Arm';
        alarmArmed.textContent = 'The alarm is disarmed';
        alarmArmed.classList.remove('connected');
        alarmArmed.classList.add('disconnected');
        message.style.display = 'none';
        document.getElementById('brokerForm').style.display = 'none';
        document.getElementById('arm').style.display = 'block';
    }
}


const checkSystemStatus = () => {
    const brokerConnected = document.getElementById('brokerStatus').classList.contains('connected');
    const alarmConnected = document.getElementById('alarmStatus').classList.contains('connected');
    const systemStatus = document.getElementById('systemStatus');
    const alarmArmed = document.getElementById('alarmArmed');
    alarmArmed.textContent = 'The alarm is disarmed';
    alarmArmed.classList.add('status-box', 'disconnected');

    if (brokerConnected && alarmConnected) {
        systemStatus.textContent = 'The alarm is on';
        systemStatus.classList.add('status-box', 'connected');
        document.getElementById('brokerStatus').style.display = 'none';
        document.getElementById('alarmStatus').style.display = 'none';
        document.getElementById('arm').style.display = 'block';
    } else {
        systemStatus.textContent = '';
        systemStatus.classList.remove('connected');
    }

}