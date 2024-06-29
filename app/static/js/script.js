let edgeCount = document.querySelectorAll('.edge-row').length - 1;

function addEdge() {
    edgeCount++;
    const edgesContainer = document.getElementById('edges-container');
    const newEdge = document.createElement('div');
    newEdge.className = 'edge-row';
    newEdge.innerHTML = `
        <label>${edgeCount}:</label>
        <input type="number" name="node1[]" required>
        <input type="number" name="node2[]" required>
        <input type="number" name="weight[]" required placeholder="Weight">
    `;
    edgesContainer.appendChild(newEdge);
}

function removeEdge() {
    if (edgeCount > 1) {
        const edgesContainer = document.getElementById('edges-container');
        edgesContainer.removeChild(edgesContainer.lastChild);
        edgesContainer.removeChild(edgesContainer.lastChild);
        edgeCount--;
    }
}

document.getElementById('generate-random-graph-btn').addEventListener('click', function() {
    generateRandomGraph();
});

document.getElementById('num_nodes').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        generateRandomGraph();
    }
});


function generateRandomGraph() {
    var numNodes = document.getElementById('num_nodes').value;
     // Validate number of nodes
    if (numNodes < 2 || numNodes > 40) {
        alert(`Number of nodes must be between 2 and 40.`);
        return;
    }
    var url = '/?num_nodes=' + encodeURIComponent(numNodes);

    // Use window.location.href to reload the page with the new parameters
    window.location.href = url;
}

document.getElementById('generate-demo-btn').addEventListener('click', function() {
    fetch('/generate_photos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            const modal = document.getElementById('errorModal');
            modal.style.display = "block";
        } else {
            const photosContainer = document.getElementById('new-demo-container');
            photosContainer.innerHTML = '';  // Clear previous photos

            data.photos.forEach((photo, index) => {
                const frameWrapper = document.createElement('div');
                frameWrapper.className = 'photo-frame';

                const img = document.createElement('img');
                img.src = 'data:image/png;base64,' + photo;
                img.alt = 'Generated Photo';
                img.className = 'photo';

                frameWrapper.appendChild(img);

                if (data.messages && data.messages[index] && data.messages[index].length) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message';

                    data.messages[index].forEach(line => {
                        const lineElem = document.createElement('div');
                        if (line.is_title) {
                            lineElem.className = 'title';
                            lineElem.innerText = line.text;
                        } else {
                            lineElem.innerText = line.text;
                        }
                        messageDiv.appendChild(lineElem);
                    });

                    frameWrapper.appendChild(messageDiv);
                }

                photosContainer.appendChild(frameWrapper);
            });
        }
    })
    .catch(error => console.error('Error:', error));
});


// Close the modal when the user clicks on <span> (x)
document.querySelector('.close').onclick = function() {
    document.getElementById('errorModal').style.display = "none";
}

// Close the modal when the user clicks anywhere outside of the modal
window.onclick = function(event) {
    const modal = document.getElementById('errorModal');
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

document.getElementById('read-more').addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('short-description').style.display = 'none';
    document.getElementById('full-description').style.display = 'block';
});

document.getElementById('read-less').addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('full-description').style.display = 'none';
    document.getElementById('short-description').style.display = 'block';
});


function getNodeNumbers() {
    const nodeNumbers = new Set();
    const edgeRows = document.querySelectorAll('.edge-row:not(.header)');

    edgeRows.forEach(row => {
        const node1 = parseInt(row.querySelector('input[name="node1[]"]').value);
        const node2 = parseInt(row.querySelector('input[name="node2[]"]').value);
        if (!isNaN(node1)) nodeNumbers.add(node1);
        if (!isNaN(node2)) nodeNumbers.add(node2);
    });

    console.log("Node numbers:", Array.from(nodeNumbers));
    return nodeNumbers;
}

function validateNodes(event) {
    event.preventDefault(); // Prevent form from submitting immediately
    console.log("Validation started");

    const nodeNumbers = getNodeNumbers();
    const startNode = parseInt(document.getElementById('start_node').value);
    const goalNode = parseInt(document.getElementById('goal_node').value);

    console.log("Start node:", startNode);
    console.log("Goal node:", goalNode);

    if (!nodeNumbers.has(startNode)) {
        alert(`Start Node ${startNode} is not found in the nodes provided.`);
        return;
    }

    if (!nodeNumbers.has(goalNode)) {
        alert(`Goal Node ${goalNode} is not found in the nodes provided.`);
        return;
    }

    console.log("Validation passed, submitting form");
    event.target.submit();
}

// Add event listener when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded");
    const form = document.querySelector('.graph-form');
    if (form) {
        console.log("Form found, adding event listener");
        form.addEventListener('submit', validateNodes);
    } else {
        console.log("Form not found");
    }
});