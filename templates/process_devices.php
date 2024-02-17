<?php
// Database configuration
$servername = "localhost";
$username = "phpmyadmin";
$password = "2002";
$dbname = "scan";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Prepare the statement
$stmt = $conn->prepare("INSERT INTO devices (ip_address, device_type, username, password) VALUES (?, ?, ?, ?)");

// Loop through each device
foreach ($_POST['ip_address'] as $ip) {
    $device_type = $_POST['device_type'][$ip];
    $username = $_POST['username'][$ip];
    $password = $_POST['password'][$ip]; // Consider securing passwords appropriately
    
    // Bind and execute
    $stmt->bind_param("ssss", $device_type, $ip, $username, $password);
    $stmt->execute();
}

echo "Device details successfully sent to the database.";

$stmt->close();
$conn->close();
?>
