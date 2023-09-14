import frida

try:
  session = frida.attach("DJIService.exe")
except frida.ProcessNotFoundError:
  print("ERROR: DJIService.exe is not running.")
  import sys
  sys.exit(1)

print("Attached to DJIService.exe")

script = session.create_script("""
const qurl_tostring = function() {
  const resolver = new ApiResolver('module');
  const matches = resolver.enumerateMatches('exports:Qt5Core.dll!?toString@QUrl@*');  // mangled name
  if (matches.length != 1) {
    console.log("Matches:");
    for (let i = 0; i < matches.length; ++i) {
      const match = matches[i];
      console.log("match: " + match.name + " " + match.address);
    }
    console.log("");
    throw new Error("Found more than one match for QUrl::toString");
  }
  return matches[0];
} ();

console.log("Found the QUrl::toString function at " + qurl_tostring.address);

Interceptor.attach(qurl_tostring.address, {
  onLeave(retval) {
    // retval should be eax
    const qstring = retval;

    // QString has QStringData pointer as the first member.
    // QStringData members (all 4 bytes)
    //    refcount - unused
    //    size
    //    offset
    // then shifted by offset we have 16-bit text.
    //
    // https://codebrowser.dev/qt5/qtbase/src/corelib/text/qstring.h.html#QString
    // https://codebrowser.dev/qt5/qtbase/src/corelib/text/qstringliteral.h.html#QStringData
    //
    const qstringdata = qstring.readPointer();
    const refcount = qstringdata.add(0).readU32();
    const size =     qstringdata.add(4).readU32();
    const offset =   qstringdata.add(12).readU32();
    const text =     qstringdata.add(offset).readUtf16String(size);

    /*
      // Debug prints.
      console.log("qstring: ", qstring);
      console.log("qstringdata: ", qstringdata);
      console.log("refcount: ", refcount);
      console.log("size: ", size);
      console.log("offset: ", offset);
      console.log("text: ", text);
    */

    console.log(text);
    console.log();
  },
});

console.log("Attached. Will print all results of QUrl::toString() calls.");

""")


def on_message(message, data):
  # only used for errors, but there shouldn't be any errors.
  print("[on_message] message:", message, "data:", data)

script.on("message", on_message)
script.load()

print()
print("Press Enter to quit this script.")
print()
input()
