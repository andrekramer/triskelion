document.addEventListener('DOMContentLoaded', function() {
    const clearButton = document.getElementById('promptButton');
    const responseList = document.getElementById('responseList');

    clearButton.addEventListener('click', function() {
        responseList.innerHTML = ''; // Empty the list
    });
});
