module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',      // new feature
        'fix',       // bug fix
        'docs',      // documentation
        'style',     // formatting
        'refactor',  // code refactoring
        'perf',      // performance
        'test',      // tests
        'chore',     // maintenance
        'ci',        // CI/CD changes
      ],
    ],
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'type-case': [2, 'always', 'lowercase'],
    'type-empty': [2, 'never'],
  },
};
