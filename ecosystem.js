module.exports = {
    apps: [
        {
            name: 'bblivelo2',
            script: '/root/correios/wsgi.py',
            interpreter: 'python3.8',
            watch: true,
            ignore_watch: ['__pycache__', 'node_modules', '*.log', 'flask_session'],
            env: {
                FLASK_ENV: 'production',
                APP_SETTINGS_MODULE: 'config.production',
                SECRET_KEY: 'mysecretkey'
            }
        }
    ]
}