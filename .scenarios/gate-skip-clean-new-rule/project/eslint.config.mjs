export default [
    {
        files: ['src/**/*.js'],
        ignores: ['src/auth/**'],
        rules: {
            'no-restricted-syntax': [
                'error',
                {
                    selector: 'ImportDeclaration[source.value=/auth.internal/]',
                    message: 'Import auth through src/auth/index.js, never its internals.',
                },
            ],
        },
    },
];
