module.exports = {
  apps: [
    {
      name: 'newsforge-api',
      script: 'python3',
      args: 'start_api.py',
      cwd: './newsforge-pro/backend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: '/Users/alphabridge/collector/newsforge-pro/backend',
        PORT: 8000
      },
      error_file: './logs/api-error.log',
      out_file: './logs/api-out.log',
      log_file: './logs/api-combined.log',
      time: true
    },
    {
      name: 'newsforge-web',
      script: 'npm',
      args: 'start',
      cwd: './news-to-social-web',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: './logs/web-error.log',
      out_file: './logs/web-out.log',
      log_file: './logs/web-combined.log',
      time: true
    }
  ]
}; 