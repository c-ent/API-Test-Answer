const express = require('express');
const fs = require('fs');
const app = express();
const { getDistance } = require('geolib');
const path = require('path');

let snapshotData = [];

const snapshotPath = path.join(__dirname, './data/snapshots/day_2.json');

// Function to load data from the file
function loadData() {
    if (fs.existsSync(snapshotPath) && fs.statSync(snapshotPath).size !== 0) {
        delete require.cache[require.resolve(snapshotPath)];
        try {
            snapshotData = require(snapshotPath);
        } catch (error) {
            console.error(`Failed to load snapshot data: ${error}`);
        }
    }
}

// Load snapshot
loadData();

// Watch for changes in the file
fs.watchFile(snapshotPath, (curr, prev) => {
    // If the file time is modifed, reload the data
    if (curr.mtime !== prev.mtime) {
        loadData();
    }
    
});


app.use(express.json({ limit: '50mb' }));
// app.use(express.urlencoded({ extended: true, limit: '50mb' }));


// Endpoint to update properties
app.post('/update_properties', (req, res) => {
    try {
        const data = req.body;
        fs.writeFileSync('received_properties.json', JSON.stringify(data, null, 4));
        res.status(200).json({ message: 'Properties updated successfully', properties: data });
    } catch (e) {
        res.status(500).json({ message: 'An error occurred: ' + e.toString() });
    }
});

// GET endpoint to fetch properties within a 65-mile radius of given coordinates
app.get('/properties_within_radius', (req, res) => {
    const { latitude, longitude } = req.query;
    
    if (!latitude || !longitude) {
        return res.status(400).json({ message: 'Latitude and longitude are required parameters.' });
    }

    const propertiesWithinRadius = snapshotData.filter(property => {
        const distance = getDistance(
            { latitude: property.latitude, longitude: property.longitude },
            { latitude: parseFloat(latitude), longitude: parseFloat(longitude) }
        );
        // Convert distance from meters to miles
        const distanceInMiles = distance * 0.000621371;
        return distanceInMiles <= 65;
    });

    res.status(200).json({ propertiesWithinRadius });
});

app.listen(5000, () => {
    console.log('Server is running on port 5000');
});
