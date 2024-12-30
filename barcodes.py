import arcpy
import qrcode
import os

# تحديد مسارات البيانات
polygon_layer = r"D:\Project"  # مسار ملف المضلع
output_point_layer = r"D:\Project"  # مسار ملف النقاط
output_folder = r"D:\Project"  # مسار مجلد تخزين الباركود

# تعريف نظم الإحداثيات
source_sr = arcpy.SpatialReference("KSA-GRF17 UTM Zone 38N")  # نظام إحداثيات الطبقة الأصلية
target_sr = arcpy.SpatialReference(4326)  # WGS84

# 1. تحويل المضلعات إلى نقاط
arcpy.FeatureToPoint_management(polygon_layer, output_point_layer, "INSIDE")

# 2. إضافة حقل للروابط
field_name = "GoogleMap"
arcpy.AddField_management(output_point_layer, field_name, "TEXT", field_length=250)

# حساب الإحداثيات وإنشاء الروابط
with arcpy.da.UpdateCursor(output_point_layer, ["SHAPE@", field_name]) as cursor:
    for row in cursor:
        # تحويل الإحداثيات إلى WGS84
        geometry = row[0].projectAs(target_sr)
        x, y = geometry.centroid.X, geometry.centroid.Y  # الإحداثيات الجغرافية
        google_maps_link = f"https://www.google.com/maps?q={y},{x}"  # صيغة الرابط
        row[1] = google_maps_link
        cursor.updateRow(row)

# 3. إنشاء الباركود
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

with arcpy.da.SearchCursor(output_point_layer, [field_name, "NEW_ID"]) as cursor:
    for row in cursor:
        link = row[0]
        fid = row[1]
        # إنشاء الباركود
        qr = qrcode.make(link)
        barcode_path = os.path.join(output_folder, f"{fid}.png")
        qr.save(barcode_path)



