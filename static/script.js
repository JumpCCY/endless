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
