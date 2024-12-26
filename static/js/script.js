document.addEventListener('DOMContentLoaded', function() {
    const clearButton = document.getElementById('promptButton');
    const responseList = document.getElementById('responseList');
    const responseHeader = document.getElementById('responseHeader');
    
    clearButton.addEventListener('click', function() {
        responseHeader.innerHTML = '';
        responseList.innerHTML = ''; // Empty the list
    });
});
