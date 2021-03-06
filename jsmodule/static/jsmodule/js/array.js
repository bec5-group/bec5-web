// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
    if (from)
        from = parseInt(from);
    if (to)
        to = parseInt(to);
    var rest = this.slice((to || from) + 1 || this.length);
    this.length = from < 0 ? this.length + from : from;
    return this.push.apply(this, rest);
};
