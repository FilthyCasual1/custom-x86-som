import ctypes as c,pathlib
l=c.CDLL('libarchive.so.13');l.archive_read_new.restype=c.c_void_p
for n in ['archive_read_support_format_all','archive_read_support_filter_all','archive_read_free']:getattr(l,n).argtypes=[c.c_void_p]
l.archive_read_add_passphrase.argtypes=[c.c_void_p,c.c_char_p];l.archive_read_open_filename.argtypes=[c.c_void_p,c.c_char_p,c.c_size_t];l.archive_read_next_header.argtypes=[c.c_void_p,c.POINTER(c.c_void_p)];l.archive_entry_pathname.argtypes=[c.c_void_p];l.archive_entry_pathname.restype=c.c_char_p;l.archive_read_data.argtypes=[c.c_void_p,c.c_void_p,c.c_size_t];l.archive_read_data.restype=c.c_ssize_t
p=l.archive_read_new();l.archive_read_support_format_all(p);l.archive_read_support_filter_all(p);l.archive_read_add_passphrase(p,b'indiafix');print('open',l.archive_read_open_filename(p,b'docs/reference/h310-boardview.rar',10240));e=c.c_void_p()
while l.archive_read_next_header(p,c.byref(e))==0:
 name=l.archive_entry_pathname(e).decode();buf=c.create_string_buffer(65536);out=bytearray()
 while True:
  n=l.archive_read_data(p,buf,65536)
  if n<=0:break
  out+=buf.raw[:n]
 print(name,len(out));pathlib.Path('docs/reference/'+pathlib.Path(name).name).write_bytes(out)
l.archive_read_free(p)
