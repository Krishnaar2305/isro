
const ana = document.getElementById("analysis");
const curr = document.getElementById("curr");
const currImg = document.getElementById("currGraph")
const uploadBtn = document.getElementById("upload")
const uploadForm = document.getElementById("uploadForm");
const buttons = document.querySelectorAll("#buttons button");
const dataBtn = document.getElementById("data")
const ogBtn = document.getElementById("original")
const smtBtn = document.getElementById("smoothened")
const peakBtn = document.getElementById("peaks")
const jsonElem = document.getElementById('jsonElem');

// const readTxt = async (name) => {
//     const resp = await fetch(`./arrayTxt/${name}`);
//     if (!resp.ok) {
//         throw new Error('Network response was not ok');
//     }
//     const text = await resp.text(); // Use .text() for reading .txt files
//     return text.split(' ').map(Number); // Convert lines to an array of numbers
// };

// let i = 0;
// if(!localStorage.getItem("size")){
//     localStorage.setItem("size", 0);
// }
// else{
//     i = parseInt(localStorage.getItem("size"));
// }

let data = {}
// const getNum = async() =>{
//     const numResp = await fetch("api/number")
//     const numJson = await numResp.json()
//     return numJson
// }


// Function to generate the Upload section
// Event listener for toggling content sections

// uploadBtn.addEventListener("click", () => {
//     i++;
//     localStorage.setItem("size", i)
//     currImg.src = `./history/img${i}.png`
// })

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent page refresh

    const formData = new FormData(uploadForm);
    
    // Use fetch to send the form data to your server
    try {
        const response = await fetch(uploadForm.action, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Handle the response (you might want to show a success message)
        const result = await response.json();
        console.log(result); 
        const tableData = genTable(result)
        updateImages(result, tableData);
        // Assuming the server responds with the image path
         // Update this based on your server response
    } catch (error) {
        console.error('Error uploading file:', error);
        // Display an error message to the user
    }
});

// buttons.forEach(button => {
//     button.addEventListener("click", function() {
//         // Remove 'active' class from all buttons
//         buttons.forEach(btn => {
//             btn.classList.remove("active");
//         });

//         // Add 'active' class to the clicked button
//         this.classList.add("active");
//     });
// });
// hist.addEventListener("click", () => {
//     getNum()
//         .then(data => {
//             const count = data.num;
//         })
// })
const updateImages = (data, text) => { 
    if (data) {
        dataBtn.classList.add("active"); 
        ogBtn.classList.remove("active"); 
        smtBtn.classList.remove("active");
        peakBtn.classList.remove("active");
        jsonElem.innerHTML = text; // Set the initial text in the jsonElem
        currImg.src = ""; // Clear current image source

        // Event listener for button clicks
        document.addEventListener("click", (event) => {
            if (event.target === dataBtn) {
                jsonElem.innerHTML = text; // Show the text for data
                currImg.src = ""; // Clear the current image
                dataBtn.classList.add("active"); // Highlight active button
                ogBtn.classList.remove("active"); // Remove highlight from other buttons
                smtBtn.classList.remove("active");
                peakBtn.classList.remove("active");

            }
            else if (event.target === ogBtn) {
                currImg.src = data.originalCurve; // Set image to original curve
                jsonElem.innerHTML = ''; // Clear the jsonElem text
                ogBtn.classList.add("active"); // Highlight active button
                dataBtn.classList.remove("active");
                smtBtn.classList.remove("active");
                peakBtn.classList.remove("active");

            } 
            else if (event.target === smtBtn) {
                currImg.src = data.smoothenedCurve; // Set image to smoothened curve
                jsonElem.innerHTML = ''; // Clear the jsonElem text
                smtBtn.classList.add("active"); // Highlight active button
                dataBtn.classList.remove("active");
                ogBtn.classList.remove("active");
                peakBtn.classList.remove("active");

            } 
            else if (event.target === peakBtn) {
                currImg.src = data.peaksCurve; // Set image to peaks curve
                jsonElem.innerHTML = ''; // Clear the jsonElem text
                peakBtn.classList.add("active"); // Highlight active button
                dataBtn.classList.remove("active");
                ogBtn.classList.remove("active");
                smtBtn.classList.remove("active");
            }
        });
    }
};


const genTable = (result) => {
    let tableData = `
    <table>
        <tr>
            <th>S.No</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Peak Time</th>
            <th>Start Value</th>
            <th>End Value</th>
            <th>Peak Value</th>
            <th>Burst Duration</th>
            <th>Burst Amplitude</th>
        </tr>
`;

    let numEntries = result.data["start_time"].length; 

    for (let i = 0; i < numEntries; i++) {
        tableData += `
            <tr>
                <td>${i + 1}</td>
                <td>${result.data["start_time"][i]}</td>
                <td>${result.data["end_time"][i]}</td>
                <td>${result.data["peak_time"][i]}</td>
                <td>${result.data["start_value"][i]}</td>
                <td>${result.data["end_value"][i]}</td>
                <td>${result.data["peak_value"][i]}</td>
                <td>${result.data["burst_duration"][i]}</td>
                <td>${result.data["burst_amplitude"][i]}</td>
            </tr>
        `;
    }

    tableData += `</table>`;

    return tableData
}