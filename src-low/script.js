function performSearch() {
    const query = document.getElementById('search-query').value;
    let searchUrl;
    searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;

    window.location.href = searchUrl;
}

function checkEnter(event) {
    if (event.key === 'Enter') {
        performSearch();
    }
}

// Функция для смены фона в зависимости от времени суток
function setBackground() {
    const hour = new Date().getHours();
    const body = document.body;

    if (hour >= 18 || hour < 6) {
        // Массив с именами файлов для вечерних фонов
        const nightBackgrounds = [
            'icons/wallpapers/background_night1.jpg',
            'icons/wallpapers/background_night2.jpg',
            'icons/wallpapers/background_night3.jpg',
            'icons/wallpapers/background_night4.jpg',
            'icons/wallpapers/background_night5.jpg',
            'icons/wallpapers/background_night6.jpg'
        ];

        // Выбор случайного фона
        const randomIndex = Math.floor(Math.random() * nightBackgrounds.length);
        body.style.backgroundImage = `url('${nightBackgrounds[randomIndex]}')`;
    } else {
        // День (6:00 - 18:00)
        body.style.backgroundImage = "url('background.jpg')";
    }
}

// Вызов функции при загрузке страницы
setBackground();

// Функция для проверки, находится ли текущая дата в заданном промежутке
function isSnowingSeason() {
    const now = new Date();
    const start = new Date(now.getFullYear(), 11, 20); // 20 декабря
    const end = new Date(now.getFullYear() + (now.getMonth() === 11 && now.getDate() > 10 ? 1 : 0), 0, 10); // 10 января
    return now >= start && now <= end;
}

// Функция для создания снежинки
function createSnowflake() {
    const snowflake = document.createElement('div');
    snowflake.classList.add('snowflake');
    snowflake.textContent = '❄';
    document.body.appendChild(snowflake);

    // Устанавливаем случайную позицию
    const startX = Math.random() * window.innerWidth;
    const duration = Math.random() * 3 + 2; // Время падения (2–5 секунд)
    const size = Math.random() * 10 + 10; // Размер снежинки (10–20px)

    snowflake.style.left = `${startX}px`;
    snowflake.style.animationDuration = `${duration}s`;
    snowflake.style.fontSize = `${size}px`;

    // Удаляем снежинку, когда анимация завершится
    snowflake.addEventListener('animationend', () => {
        snowflake.remove();
    });
}

// Запускаем снегопад, если текущая дата в пределах периода
if (isSnowingSeason()) {
    setInterval(createSnowflake, 200);
} else {
    console.log("Снегопад работает с 20 декабря до 10 января.");
}
