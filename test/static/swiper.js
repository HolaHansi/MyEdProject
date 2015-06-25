<!-- Initialize Swiper -->
var appendNumber = 1;
var prependNumber = 1;
var swiper = new Swiper('.swiper-container', {
//  pagination: '.swiper-pagination',
    nextButton: '.swiper-button-next',
    prevButton: '.swiper-button-prev',
    slidesPerView: 1,
    centeredSlides: false,
//  paginationClickable: true,
    spaceBetween: 30,
});

//appending slides
document.querySelector('.swiper-button-next').addEventListener('click', function (e) {
    e.preventDefault();
    console.log(appendNumber);
    if (++appendNumber < noOfLocations) {
        swiper.appendSlide('<div class="swiper-slide"> ' + "<iframe id='innerContent' class='currentMap map-top' width='100%' height='100%' src=" + "https://www.google.com/maps/embed/v1/directions?key=" + API_KEY + "&origin=" + userLatitude + ',' + userLongitude + "&destination=" + destinationLatitudes[appendNumber] + ',' + destinationLongitudes[appendNumber] + "&mode=walking" + "></iframe>" + '</div>');
    }
});