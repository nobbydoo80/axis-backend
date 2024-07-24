module.exports = {
  preset: 'jest-puppeteer',
  setupFilesAfterEnv: ['./jest.setup.js'],
  roots: [
    '../axis',
  ],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
  },
  globals: {
    SITE_URL: process.env.QA_HOST || 'http://localhost:8000',
    SUPERUSER_USERNAME: process.env.QA_SUPERUSER_USERNAME || 'admin',
    SUPERUSER_PASSWORD: process.env.QA_SUPERUSER_PASSWORD || 'password',
  },
  transform: {
    "^.+\\.jsx?$": "babel-jest"
  },
}
