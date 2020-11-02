document.querySelectorAll('.accordion__button').forEach(button=>{
    button.addEventListener('click', () => {
        button.classList.toggle('accordion__button--active');
    })
})