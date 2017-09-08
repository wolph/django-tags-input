# jQuery Tags Input Revisited Plugin

## Basic information

Forked from discontinued jQuery Tags Input Plugin created by [XOXCO](http://xoxco.com).

See the original project here: https://github.com/xoxco/jQuery-Tags-Input

jQuery Tags Input Revisited Plugin is an improved and fixed version of the previous plugin. It's also adjusted to match the current web standards.

Simple tag editing written in jQuery.

Original description: Do you use tags to organize content on your site? This plugin will turn your boring tag list into a magical input that turns each tag into a style-able object with its own delete link. The plugin handles all the data - your form just sees a comma-delimited list of tags!

## Improvements

jQuery Tags Input Revisited welcomes few very important improvements:

1. It switches input width adjustment from JS to flexbox.
2. It manipulates styles with CSS not JS.
3. It uses standard placeholder instead of input value.
4. It uses CSS for remove link not text.
5. It adds better validation for min/max string length, tags limit and pattern validation.
6. It uses CSS matching current standards.
7. It adds copy/paste mechanism that automatically splits the string into tags.

## Usage

Add the Javascript and CSS files to the HTML. You can use regular or minified files. Style the tags however you want.

```
<script src="jquery.tagsinput-revisited.js"></script>
<link rel="stylesheet" type="text/css" href="jquery.tagsinput-revisited.css">
```

Create a real input in your form that will contain a delimiter-separated (by standard it's a comma) list of tags. You can put any default or existing tags in the value attribute, and they'll be handled properly.

```
<input name="tags" id="tags" class="tagsinput" value="foo,bar,baz">
```

Then, simply call the tagsInput function on any field that should be treated as a list of tags.

```
$('.tagsinput').tagsInput();
```

If you want to use jQuery.autocomplete, you can pass an object with autocomplete options (https://jqueryui.com/autocomplete/).

```
$('.tagsinput').tagsInput({
  autocomplete: {option: value, option: value}
});
```

You can add and remove tags by calling the addTag() and removeTag() functions.

```
$('.tagsinput#tags').addTag('foo');
$('.tagsinput#tags').removeTag('bar');
```

You can import a list of tags using the importTags() function.

```
$('.tagsinput#tags').importTags('foo, bar, baz');
```

You can also use importTags() to reset the tag list.

```
$('.tagsinput#tags').importTags('');
```

And you can check if a tag exists using tagExist().

```
$('.tagsinput#tags').tagExist('foo')) { ... }
```

If additional functionality is required when a tag is added or removed, you may specify callback functions via the `onAddTag` and `onRemoveTag` parameters. Both functions should accept a single tag as the parameter.

If you do not want to provide a way to add tags, or you would prefer to provide an alternate interface for adding tags to the box, you may pass an false into the optional `interactive` parameter. The tags will still be rendered as per usual, and the `addTag` and `removeTag` functions will operate as expected.

If you want a function to be called every time a tag is updated/deleted, set it as the `onChange` option.

By default, if the cursor is immediately after a tag, hitting backspace will delete that tag. If you want to override this, set the `removeWithBackspace` option to false.

For validation purposes you an use `unique`, `limit`, `minChars`, `maxChars` and `validationPattern` parameters.

You can check `example.html` file to see the plugin usage examples.

## Options

```
$('.tagsinput#tags').tagsInput({
  interactive: true,
  placeholder: 'Add a tag',
  minChars: 2,
  maxChars: 20, // if not provided there is no limit
  limit: 5, // if not provided there is no limit
  validationPattern: new RegExp('^[a-zA-Z]+$'), // a pattern you can use to validate the input
  width: '300px', // standard option is 'auto'
  height: '100px', // standard option is 'auto'
  autocomplete: { option: value, option: value},
  hide: true,
  delimiter: [',',';'], // or a string with a single delimiter. Ex: ';'
  unique: true,
  removeWithBackspace: true,
  onAddTag: callback_function,
  onRemoveTag: callback_function,
  onChange: callback_function
});
```

## About the author

* [underovsky.com](http://underovsky.com)
* [twitter.com/underovsky](https://twitter.com/underovsky)
* [facebook.com/underovsky](https://facebook.com/underovsky)

## License

The MIT License (MIT)

Copyright (c) 2015 Krzysztof Rusnarczyk
