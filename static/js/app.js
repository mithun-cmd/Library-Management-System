// ======================================================
// SEARCH FILTERS
// ======================================================

const studentSearch = document.getElementById("studentSearch");

if(studentSearch){

    studentSearch.addEventListener("keyup", function(){

        let value =
        this.value.toLowerCase();

        let rows =
        document.querySelectorAll(
            "#studentsTable tbody tr"
        );

        rows.forEach(row => {

            row.style.display =
            row.innerText.toLowerCase().includes(value)
            ? ""
            : "none";

        });

    });

}

// ======================================================

const bookSearch = document.getElementById("bookSearch");

if(bookSearch){

    bookSearch.addEventListener("keyup", function(){

        let value =
        this.value.toLowerCase();

        let rows =
        document.querySelectorAll(
            "#booksTable tbody tr"
        );

        rows.forEach(row => {

            row.style.display =
            row.innerText.toLowerCase().includes(value)
            ? ""
            : "none";

        });

    });

}

// ======================================================
// DARK MODE
// ======================================================

const themeBtn =
document.querySelector(".theme-btn");

themeBtn.addEventListener("click", () => {

    document.body.classList.toggle("dark-mode");

});

// ======================================================
// AUTO HIDE FLASH
// ======================================================

setTimeout(() => {

    let flashes =
    document.querySelectorAll(".flash-message");

    flashes.forEach(flash => {

        flash.style.opacity = "0";

        flash.style.transform =
        "translateY(-10px)";

        setTimeout(() => {

            flash.remove();

        }, 500);

    });

}, 3000);


// ======================================================
// PAGE LOADER
// ======================================================

window.addEventListener("load", () => {

    const loader =
    document.getElementById("loader-wrapper");

    loader.style.opacity = "0";

    setTimeout(() => {

        loader.style.display = "none";

    }, 500);

});