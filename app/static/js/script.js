// add hovered class to selected list item
let list = document.querySelectorAll(".sidenav li");

function activeLink() {
  list.forEach((item) => {
    item.classList.remove("hovered");
  });
  this.classList.add("hovered");
}

list.forEach((item) => item.addEventListener("mouseover", activeLink));

// Menu Toggle
let toggle = document.querySelector(".toggle");
let sidenav = document.querySelector(".sidenav");
let topnav = document.querySelector(".topnav");
let outer = document.querySelector(".outer");

toggle.onclick = function () {
  topnav.classList.toggle("active");
  sidenav.classList.toggle("active");
  outer.classList.toggle("active");
};
