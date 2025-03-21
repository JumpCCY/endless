async function stockCheck(item_id) {
    const table = document.querySelectorAll(`.stock_table_row_${item_id}`);
    try {
        const response = await fetch(`/stock_check?item_id=${item_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        });

        return await response.json();
    } catch (error) {
        console.error(`Error catching data`, error);
    }
}

function tableHinder(item_id) {
    const table = document.querySelectorAll(`.stock_table_row_${item_id}`);
    table.forEach((table) => {
        if (table.style.display === "none" || table.style.display === "") {
            table.style.display = "table-row";
        } else {
            table.style.display = "none";
        }
    });
}

function createTable(item_id) {
    stockCheck(item_id).then(data => {
        var size_id = 1
        data.forEach(row => {
            document.getElementById(`itemID_${item_id}_sizeID_${size_id}`).innerText = `${row.quantity}`;
            size_id++;
        });
    });

}

function updateSizeTable(item_id, size_id) {

}

function add(item_id, size_id) {
    const quantity = document.getElementById(`amount_itemID_${item_id}_sizeID_${size_id}`).value;
    document.getElementById(`amount_itemID_${item_id}_sizeID_${size_id}`).value = '';
    fetch(`/add_specific_size_quantity?item_id=${item_id}&size_id=${size_id}&quantity=${quantity}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);  // Show error message
            } else {
                document.getElementById(`itemID_${item_id}_sizeID_${size_id}`).innerText = data;
            }
        }).catch(error => {
        console.error("Error: ", error);
    })
}

function remove(item_id, size_id) {
    const quantity = document.getElementById(`amount_itemID_${item_id}_sizeID_${size_id}`).value;
    document.getElementById(`amount_itemID_${item_id}_sizeID_${size_id}`).value = '';
    fetch(`/remove_specific_size_quantity?item_id=${item_id}&size_id=${size_id}&quantity=${quantity}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);  // Show error message
            } else {
                document.getElementById(`itemID_${item_id}_sizeID_${size_id}`).innerText = data;
            }
        }).catch(error => {
        console.error("Error: ", error);
    })
}

function editPriceButtonHandler(item_id, price) {
    const element = document.getElementById(`price_${item_id}`);
    const edit_button = document.getElementById(`edit_price_button_${item_id}`);

    if (edit_button.innerHTML === `Cancel`) {
        element.innerHTML = price;
        edit_button.innerHTML = `Edit price`;
    } else {
        edit_button.innerHTML = `Cancel`;
        element.innerHTML = `<input type="number" id="editInput_${item_id}" value="" placeholder="New price" autofocus> <button type="button" onclick="editPrice(${item_id})">Confirm</button>`;

    }
}

function editPrice(item_id) {
    const new_price = document.getElementById(`editInput_${item_id}`).value;

    fetch(`/change_price?item_id=${item_id}&price=${new_price}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(r => response => r.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                location.reload();
            }
        }).catch(error => {
        console.error("Error: ", error);
    })
}

let input = document.getElementById("INDEX")
input.addEventListener("input", async function () {


    try {
        let response = await fetch(`/search?q=${input.value}`);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        let data = await response.json();
        console.log(data)


let searchBox = document.getElementById("results");
        if (input.value === "") {
            searchBox.innerHTML = "";
        }
        else if (data.length < 1) {

            searchBox.innerHTML = "";
            let h3 = document.createElement("h3");

            let text = document.createTextNode("Couldn't find the result");

            h3.appendChild(text);
            searchBox.appendChild(h3);
        }
        else {
            searchBox.innerHTML = "";
            // Create table header
            let table = document.createElement('table');
            let thead = document.createElement('thead');
            let headerRow = document.createElement('tr');
            headerRow.innerHTML = `
        <th>Item</th>
        <th>Version</th>
        <th>Price</th>
    `;
            thead.appendChild(headerRow);
            table.appendChild(thead);

            // Create table body
            let tbody = document.createElement('tbody');
            data.forEach(item => {
                let row = document.createElement('tr');
                row.innerHTML = `
            <td>${item.Item}</td>
            <td>${item.Version}</td> 
            <td>${item.Price}</td> 
        `;
                tbody.appendChild(row);

                  // Create a second row for size details
                let sizeRow = document.createElement("tr");
                let sizeDetails = item.sizes.map(size => `Size ${size.Size}: ${size.Quantity}`).join(" | ");
                sizeRow.innerHTML = `
                    <td colspan="3" style="text-align: center;">${sizeDetails}</td>
                `;
                tbody.appendChild(sizeRow);
            });
            table.appendChild(tbody);
            searchBox.appendChild(table);
        }


    } catch (error) {
        console.error('Error:', error);
    }
});
