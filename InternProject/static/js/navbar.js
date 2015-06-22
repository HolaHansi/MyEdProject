$(document).ready(function() {
    $('.options-toggle').click(function () {
        if ($('.container-options')[0]) {
            $('.container-options').addClass('navbar-options');
            $('.container-options').removeClass('container');
            $('.container-options').removeClass('container-options');
        } else {
            $('.navbar-options').addClass('container-options');
            $('.navbar-options').addClass('container');
            $('.navbar-options').removeClass('navbar-options');
        }
    });

    $('.btn-toggle').click(function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        } else {
            $(this).addClass('selected');
        }
    });
    $('#retryBtn').click(function () {
        $('.container-options').addClass('navbar-options');
        $('.container-options').removeClass('container');
        $('.container-options').removeClass('container-options');
    });
})