let startTime = Date.now();

// Track clicks on the page
document.addEventListener('click', function (e) {
    console.log("Clicked:", e.target);
});

// Track scrolling duration
let scrollStartTime = null;
window.addEventListener('scroll', function () {
    if (!scrollStartTime) {
        scrollStartTime = Date.now();
    }
});

window.addEventListener('beforeunload', function () {
    // Log duration of scrolling and overall time spent
    const timeSpent = (Date.now() - startTime) / 1000; // seconds
    const scrollDuration = (Date.now() - scrollStartTime) / 1000; // seconds

    console.log("Time spent on page:", timeSpent);
    console.log("Scrolling duration:", scrollDuration);

    // You can send this data to the server for logging
    // Example using fetch (commented out as it's an illustration)
    /*
    fetch('/log_data', {
        method: 'POST',
        body: JSON.stringify({ timeSpent, scrollDuration }),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    */
});
