// Highlight timeline bars on hover
$(".timeline_item").mouseover(function() {
   $(this).css("border", "red 0.1px solid");
}).mouseout(function() {
   $(this).css("border", "none");
});
