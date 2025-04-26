$(document).ready(function() {
    // Add any additional client-side validation or animations if needed
    $('form').on('submit', function() {
        $(this).find('button[type="submit"]').addClass('opacity-50 cursor-not-allowed').text('Logging in...');
    });
});
