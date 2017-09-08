module.exports = function(grunt) {
	grunt.registerTask('assets:production',
	[
		'cssmin:plugin',
		'uglify:plugin',
		'file_append:plugin'
	]);
};
