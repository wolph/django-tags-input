module.exports = {
    plugin: {
	    files: [
	            {
	            	prepend: "/* jQuery Tags Input Revisited Plugin\n\n* Copyright (c) Krzysztof Rusnarczyk\n* Licensed under the MIT license */\n",
					input: 'dist/jquery.tagsinput-revisited.min.js',
					output: 'dist/jquery.tagsinput-revisited.min.js'
	            }
	    ]
    }
};
