async function loadApps() {
    const launcher = document.getElementById('launcher');

    try {
        // Simulate a scan of the "apps" directory
        const response = await fetch('apps/manifest.json');
        const apps = await response.json();

        apps.forEach(app => {
            const appElement = document.createElement('div');
            appElement.className = 'app-icon';

            const appIcon = document.createElement('img');
            appIcon.src = `apps/${app.folder}/icon.png`;
            appIcon.alt = app.name;

            const appName = document.createElement('div');
            appName.className = 'app-name';
            appName.textContent = app.name;

            appElement.appendChild(appIcon);
            appElement.appendChild(appName);

            appElement.addEventListener('click', () => {
                window.open(`apps/${app.folder}/index.html`, '_blank');
            });

            launcher.appendChild(appElement);
        });
    } catch (error) {
        console.error('Failed to load apps:', error);
    }
}

loadApps();
