import os
import sys
import optparse
import zipfile
import tarfile
import tempfile
import time
import py_compile

def zip_library(f, extra_files = []):
    lib = "%s/lib/python%s/"%(sys.prefix,sys.version[:3])
    
    zf = zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED)
    
    for root, _, files in os.walk(lib):
        arcroot = os.path.relpath(root, lib)
        for f in files:
            _, ext = os.path.splitext(f)
            if ext in ['.py']:
                zf.write(os.path.join(root,f), os.path.join(arcroot, f))

    for s, r in extra_files:
        zf.write( s, r )

    zf.close()
    
def add_python_lib(tf, lib_dir, lib, mtime):

    _, prefix = os.path.split(lib)
    
    for root, _, files in os.walk(lib):

        relpath = os.path.relpath(root, lib)

        if '.hg' in relpath.split('/'):
            continue

        if relpath=='.':
            arcroot = lib_dir
        else:
            arcroot = os.path.join( lib_dir, os.path.relpath(root, lib) )

        arcroot = os.path.join(arcroot, prefix)

        add_dir(tf, arcroot, mtime)
        
        for f in files:
            _, ext = os.path.splitext(f)
            if ext in ['.py', '.so']:
                add_file( tf, os.path.join(root,f), os.path.join(arcroot, f), 0666, mtime)

def add_dir(tf, dir, mtime):
    ti = tarfile.TarInfo(dir)
    ti.mode = 0777
    ti.mtime = mtime
    ti.type = tarfile.DIRTYPE
    
    tf.addfile(ti)

def add_fileobj(tf, f, arcname, mode, mtime):
    ti = tarfile.TarInfo(arcname)
    ti.mode = mode
    ti.mtime = mtime
    
    f.seek(0, os.SEEK_END)
    ti.size = f.tell()
    
    f.seek(0, os.SEEK_SET)
    tf.addfile(ti, f)
    
def add_file(tf, fname, arcname, mode, mtime):
    print "\t adding %s as %s"%(fname, arcname)
    
    with open(fname, "rb") as f:
        add_fileobj(tf, f, arcname, mode, mtime)

def package(dir, bin, lib, extra_files, ofname, use_sys):
    
    mtime = time.time()
    
    tf = tarfile.open(ofname, "w:gz")
    
    add_dir(tf, dir, mtime)

    if bin:

        bin_dir = os.path.join(dir, 'bin')
        add_dir(tf, bin_dir, mtime)

        for bf in bin:
            add_file( tf, bf, os.path.join(bin_dir, os.path.basename(bf)), 0777, mtime)

    if lib:

        lib_dir = os.path.join(dir, 'lib')
        add_dir(tf, lib_dir, mtime)

        for lf in lib:
            add_python_lib( tf, lib_dir, lf, mtime)
    
    for file, dest in extra_files:
        add_file(tf, file, os.path.join(dir, dest), 0666, mtime)
    
    if not use_sys:

        # ZIP standard library    
        zf = tempfile.NamedTemporaryFile("w+b")
        zip_library(zf, [])
        zf.flush()
        
        add_fileobj(tf, zf, "%s/lib/python_library.zip"%dir, 0666, mtime)
        
        zf.close()
    
        # add all extensions
        
        lib_dynload = os.path.join(sys.exec_prefix,"lib", "python%s"%sys.version[:3], "lib-dynload")
        
        for fn in os.listdir(lib_dynload):
            fullname = os.path.join(lib_dynload, fn)
            if os.path.isfile(fullname):
                add_file( tf, fullname, os.path.join("%s/lib"%dir, fn), 0666, mtime)
    
    tf.close()


def main(args):
    
    usage = "usage: %prog [options]"

    parser = optparse.OptionParser(usage)

    parser.add_option("-o", "--out", dest="out", help="location of output tar gzipped file")
    parser.add_option("-d", "--dir", dest="dir", help="name of generated directory" )

    parser.add_option("-b", "--bin", dest="bin", action='append', default=[], help="binaries to pack" )
    parser.add_option("-l", "--lib", dest="lib", action='append', default=[], help="python libraries to pack" )
    parser.add_option("-f", "--files", dest="files", action='append', default=[], help="additional files (comma separated pairs of file:dest" )

    parser.add_option("-S", "--system", action="store_false", dest="sys", default=True, help="use default python installation")

    options, args = parser.parse_args(args)

    if len(args) > 1:
        parser.print_help()
        return 1
        
    if not options.dir or not options.out:
        parser.print_help()
        return 1

    if not options.bin and not options.lib and not options.files:
        parser.print_help()
        return 1

    files = [ s.split(':') for s in options.files ]

    return package(
        options.dir,
        options.bin,
        options.lib,
        files,
        options.out,
        options.sys
    )

if __name__=="__main__":
    main(sys.argv)
