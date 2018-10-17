var gulp = require('gulp');
var $ = require('gulp-load-plugins')();
var merge = require('merge-stream');

var paths = {
    jade: 'partials/contrib/*.jade',
    coffee: 'coffee/*.coffee',
    images: 'images/**/*',
    dist: 'dist/',
    modules: 'node_modules/'
};
paths.libs = [
  paths.modules + 'url-join/lib/url-join.js'
];

paths.libs.forEach(function(file) {
    try {
        // Query the entry
        stats = fs.lstatSync(file);
    }
    catch (e) {
        console.log(file);
    }
});

gulp.task('copy-config', function() {
    return gulp.src('oidc-auth.json')
        .pipe(gulp.dest(paths.dist));
});

gulp.task('copy-images', function() {
    return gulp.src(paths.images)
        .pipe(gulp.dest(paths.dist + "images"));
});

gulp.task('compile', function() {
    var jade = gulp.src(paths.jade)
        .pipe($.plumber())
        .pipe($.cached('jade'))
        .pipe($.jade({pretty: true}))
        .pipe($.angularTemplatecache({
            transformUrl: function(url) {
                return '/plugins/oidc-auth/' + url;
            }
        }))
        .pipe($.remember('jade'));

    var coffee = gulp.src(paths.coffee)
        .pipe($.plumber())
        .pipe($.cached('coffee'))
        .pipe($.coffee())
        .pipe($.remember('coffee'));

    var libs = gulp.src(paths.libs)
        .pipe($.plumber())
        .pipe($.cached('libs'))
        .pipe($.remember('libs'));

    return merge(jade, coffee, libs)
        .pipe($.concat('oidc_auth.js'))
        .pipe($.uglify({mangle:false, preserveComments: false}))
        .pipe(gulp.dest(paths.dist));
});

gulp.task('watch', function() {
    gulp.watch([paths.jade, paths.coffee, paths.images], ['copy-images', 'compile']);
});

gulp.task('default', ['copy-config', 'copy-images', 'compile', 'watch']);

gulp.task('build', ['copy-config', 'copy-images', 'compile', ]);
