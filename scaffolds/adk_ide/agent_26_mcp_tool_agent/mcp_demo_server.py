# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import csv
import os

from fastmcp import FastMCP
from pydantic import Field

# Define the path to the CSV file relative to this script
# Assuming operations.py and sku_data.csv are in the same
# directory 'agents/inventory/'
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "sku_data.csv")

global mcp
mcp = FastMCP(
    name="Inventory MCP Server",
    instructions="""
    This Server provides inventory related data and helps in
    updating the quantity of a specific SKU.

    Call list_skus() to get the list of all the SKUs or any details related the items/SKUs.
    Call update_sku_qty(sku_id) to update the quantity of a specific SKU.
    """,
)


@mcp.tool()
def list_skus(sku_name: str = Field("*", description="Name of the SKU")):
    """
    Reads the SKU data from the CSV file and returns it as a list of dictionaries.
    If you are asked for the available items or any enquiry about the items/SKUs,
    call this function andreturn only the consumer freindly information
    like id, name and its cost and available quantity.
    """
    if not os.path.exists(CSV_FILE_PATH):
        return {"error": "SKU data file not found."}

    skus = []
    try:
        with open(CSV_FILE_PATH, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                skus.append(row)
        return {"skus": skus}
    except Exception as e:
        return {"error": f"Failed to read SKU data: {str(e)}"}


@mcp.tool()
def update_sku_qty(
    sku_id: str = Field(
        ..., description="The SKU ID of the product to update."
    ),
    quantity: int = Field(
        ...,
        description="The quantity to be added or removed from the SKU.",
        ge=0,
    ),
    sign: int = Field(1, description="1 for adding and -1 for removing."),
):
    """
    Updates the quantity of a specific SKU in the CSV file.
    If you are asked for placing or returning/cancelling an order, call this function.

    Args:
        sku_id (str): The SKU ID of the product to update.
        quantity (int): The new quantity for the SKU.
        sign (int): 1 for adding and -1 for removing.

    Returns:
        dict: A message indicating success or failure.
    """
    if not os.path.exists(CSV_FILE_PATH):
        return {"error": "SKU data file not found."}

    if not isinstance(quantity, int):
        return {"error": "Invalid quantity. Must be a non-negative integer."}

    rows = []
    updated = False
    fieldnames = []

    try:
        with open(CSV_FILE_PATH, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            if not fieldnames:  # Handle empty or malformed CSV
                return {"error": "CSV file is empty or has no header."}

            quantity *= sign

            for row in reader:
                if row.get("SKU") == sku_id:
                    row["QuantityOnHand"] = int(row["QuantityOnHand"]) + int(
                        quantity
                    )
                    # Potentially update 'Status' based on
                    # new quantity vs ReorderLevel
                    if "ReorderLevel" in row and quantity <= int(
                        row.get("ReorderLevel", 0)
                    ):
                        row["Status"] = "Low Stock"
                    elif "ReorderLevel" in row and quantity > int(
                        row.get("ReorderLevel", 0)
                    ):
                        row["Status"] = "In Stock"
                    updated = True
                    updated_qty = row["QuantityOnHand"]
                rows.append(row)

        if not updated:
            return {"error": f"SKU ID '{sku_id}' not found."}

        with open(
            CSV_FILE_PATH, mode="w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return {
            "message": f"Quantity for SKU '{sku_id}' updated to {updated_qty}."
        }
    except Exception as e:
        return {"error": f"Failed to update SKU quantity: {str(e)}"}


if __name__ == "__main__":
    asyncio.run(
        mcp.run_sse_async(
            host="0.0.0.0",
            port=4200,
            path="/inventory",
        )
    )
