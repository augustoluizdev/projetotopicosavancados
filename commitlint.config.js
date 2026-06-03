module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        'api_rest',
        'api_topicos',
        'templates',
        'infra',
        'deps',
        'ci',
        'auth',
        'events',
        'cart',
        'orders',
        'websocket',
      ],
    ],
    'subject-max-length': [2, 'always', 72],
    'subject-case': [2, 'always', 'lower-case'],
  },
};
