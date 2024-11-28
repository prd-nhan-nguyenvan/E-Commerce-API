import csv
from io import StringIO

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdminOrStaff
from products.tasks import bulk_import_products


class BulkImportProductView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminOrStaff]

    @swagger_auto_schema(
        tags=["Products"],
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="CSV file with product data",
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_data = file.read().decode("utf-8")
            csv_data = csv.DictReader(StringIO(file_data))

            required_columns = [
                "name",
                "description",
                "price",
                "sell_price",
                "on_sell",
                "stock",
                "category_name",
            ]

            if not all(col in csv_data.fieldnames for col in required_columns):
                return Response(
                    {
                        "error": f"CSV must contain the following columns: {', '.join(required_columns)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product_data_list = []
            for row in csv_data:
                if not all(row.get(col) for col in required_columns):
                    return Response(
                        {"error": f"Row contains missing data: {row}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                product_data_list.append(row)

            bulk_import_products.delay(product_data_list)
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
