#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node* next;
};

struct Node* createNode(int data);
struct Node* createLinkedList();
void displayList(struct Node* head);
void insertAtBeginning(struct Node** head, int data);
void insertAtEnd(struct Node** head, int data);
void insertAtPosition(struct Node** head, int data, int position);
void deleteFromBeginning(struct Node** head);
void deleteFromEnd(struct Node** head);
void deleteAtPosition(struct Node** head, int position);
int searchElement(struct Node* head, int key);
int calculateLength(struct Node* head);
void reverseList(struct Node** head);
void sortList(struct Node** head);
void clearInputBuffer();

int main() {
    struct Node* head = NULL;
    int choice, data, position;

    // Initial step to create a linked list
    head = createLinkedList();

    do {
        printf("\n----- Linked List Operations -----\n");
        printf("1. Insert at the Beginning\n");
        printf("2. Insert at the End\n");
        printf("3. Insert at a Specific Position\n");
        printf("4. Delete from the Beginning\n");
        printf("5. Delete from the End\n");
        printf("6. Delete from a Specific Position\n");
        printf("7. Display List\n");
        printf("8. Search Element\n");
        printf("9. Calculate Length\n");
        printf("10. Reverse List\n");
        printf("11. Sort List\n");
        printf("0. Exit\n");
        printf("Enter your choice: ");

        if (scanf("%d", &choice) != 1) {
            printf("Invalid choice. Please try again.\n");
            clearInputBuffer();
            continue;
        }


        switch (choice) {
            case 1:
                printf("Enter data to insert at the beginning: ");
                // Check the return value of scanf
                if (scanf("%d", &data) != 1) {
                    printf("Invalid input. Please enter a valid integer.\n");
                    clearInputBuffer();  // Clear the input buffer
                    break;
                }
                insertAtBeginning(&head, data);
                break;
            case 2:
                printf("Enter data to insert at the end: ");
                // Check the return value of scanf
                if (scanf("%d", &data) != 1) {
                    printf("Invalid input. Please enter a valid integer.\n");
                    clearInputBuffer();  // Clear the input buffer
                    break;
                }
                insertAtEnd(&head, data);
                break;
            case 3:
                printf("Enter data to insert: ");
                // Check the return value of scanf
                if (scanf("%d", &data) != 1) {
                    printf("Invalid input. Please enter a valid integer.\n");
                    clearInputBuffer();  // Clear the input buffer
                    break;
                }
                printf("Enter position to insert at: ");
                // Check the return value of scanf
                if (scanf("%d", &position) != 1) {
                    printf("Invalid input. Please enter a valid integer.\n");
                    clearInputBuffer();  // Clear the input buffer
                    break;
                }
                insertAtPosition(&head, data, position);
                break;
            case 4:
                deleteFromBeginning(&head);
                break;
            case 5:
                deleteFromEnd(&head);
                break;
            case 6:
                printf("Enter position to delete: ");
                // Check the return value of scanf
                if (scanf("%d", &position) != 1) {
                    printf("Invalid input. Please enter a valid integer.\n");
                    clearInputBuffer();  // Clear the input buffer
                    break;
                }
                deleteAtPosition(&head, position);
                break;
            case 7:
                displayList(head);
                break;
            case 8:
                printf("Enter element to search: ");
                // Check the return value of scanf
                if (scanf("%d", &data) != 1) {
                    printf("Invalid input. Please enter a valid integer.\n");
                    clearInputBuffer();  // Clear the input buffer
                    break;
                }
                position = searchElement(head, data);
                if (position != -1)
                    printf("Element found at position %d\n", position);
                else
                    printf("Element not found\n");
                break;
            case 9:
                printf("Length of the list: %d\n", calculateLength(head));
                break;
            case 10:
                reverseList(&head);
                if (head == NULL) {
                    printf("List is empty. Nothing to reverse.\n");
                } else {
                    printf("List reversed successfully.\n");
                }
                break;
            case 11:
                sortList(&head);
                if (head == NULL) {
                    printf("List is empty. Nothing to sort.\n");
                } else {
                    printf("List sorted successfully.\n");
                }
                break;
            case 0:
                printf("Exiting program.\n");
                break;
            default:
                printf("Invalid choice. Please try again.\n");
                clearInputBuffer();  // Clear the input buffer in case of invalid input
        }
    } while (choice != 0);

    return 0;
}

struct Node* createNode(int data) {
    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));
    if (newNode == NULL) {
        printf("Memory allocation failed.\n");
        exit(EXIT_FAILURE);
    }
    newNode->data = data;
    newNode->next = NULL;
    return newNode;
}

struct Node* createLinkedList() {
    struct Node* head = NULL;
    struct Node* tail = NULL;
    char buffer[100];  // Adjust the buffer size as needed
    char *endptr;

    int n;  // Variable to store the number of elements

    do {
        printf("Enter the number of elements: ");

        // Read a line of input for the number of elements
        if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
            printf("Error reading input.\n");
            exit(EXIT_FAILURE);
        }

        // Use strtol to parse the integer
        n = strtol(buffer, &endptr, 10);

        // Check for conversion errors
        if (*endptr != '\n' && *endptr != '\0') {
            printf("Invalid input. Please enter a valid integer.\n");
        } else if (n < 0) {
            printf("Number of elements cannot be negative.\n");
            // Force loop to continue
            *endptr = 'x'; 
        }
    } while (*endptr != '\n' && *endptr != '\0');

    for (int i = 0; i < n; ++i) {
        do {
            printf("Enter element %d: ", i + 1);

            // Read a line of input for the element
            if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
                printf("Error reading input.\n");
                exit(EXIT_FAILURE);
            }

            
            long data = strtol(buffer, &endptr, 10);

            // Check for conversion errors
            if (*endptr != '\n' && *endptr != '\0') {
                printf("Invalid input. Please enter a valid integer for element %d: ", i + 1);
                clearInputBuffer();  // Clear the input buffer
            } else {
                struct Node* newNode = createNode((int)data);
                if (head == NULL) {
                    head = newNode;
                    tail = newNode;
                } else {
                    tail->next = newNode;
                    tail = newNode;
                }
                break;  // Break the loop if input is valid
            }
        } while (1);
    }

    return head;
}

// Function to display the elements of the linked list
void displayList(struct Node* head) {
    struct Node* current = head;

    if (current == NULL) {
        printf("List is empty.\n");
        return;
    }

    printf("Linked List: ");
    while (current != NULL) {
        printf("%d ", current->data);
        current = current->next;
    }
    printf("\n");
}

// Function to insert a node at the beginning of the linked list
void insertAtBeginning(struct Node** head, int data) {
    struct Node* newNode = createNode(data);
    newNode->next = *head;
    *head = newNode;
    printf("Element inserted at the beginning.\n");
}

// Function to insert a node at the end of the linked list
void insertAtEnd(struct Node** head, int data) {
    struct Node* newNode = createNode(data);
    if (*head == NULL) {
        *head = newNode;
    } else {
        struct Node* current = *head;
        while (current->next != NULL) {
            current = current->next;
        }
        current->next = newNode;
    }
    printf("Element inserted at the end.\n");
}

// Function to insert a node at a specified position in the linked list
void insertAtPosition(struct Node** head, int data, int position) {
    if (position < 1) {
        printf("Invalid position. Position should be >= 1.\n");
        return;
    }

    if (position == 1) {
        insertAtBeginning(head, data);
        return;
    }

    struct Node* newNode = createNode(data);
    struct Node* current = *head;
    for (int i = 1; i < position - 1 && current != NULL; ++i) {
        current = current->next;
    }

    if (current == NULL) {
        printf("Position out of bounds.\n");
    } else {
        newNode->next = current->next;
        current->next = newNode;
        printf("Element inserted at position %d.\n", position);
    }
}

// Function to delete a node from the beginning of the linked list
void deleteFromBeginning(struct Node** head) {
    if (*head == NULL) {
        printf("List is empty. Nothing to delete.\n");
        return;
    }

    struct Node* temp = *head;
    *head = (*head)->next;
    free(temp);
    printf("Element deleted from the beginning.\n");
}

// Function to delete a node from the end of the linked list
void deleteFromEnd(struct Node** head) {
    if (*head == NULL) {
        printf("List is empty. Nothing to delete.\n");
        return;
    }

    if ((*head)->next == NULL) {
        free(*head);
        *head = NULL;
        printf("Element deleted from the end.\n");
        return;
    }

    struct Node* current = *head;
    while (current->next->next != NULL) {
        current = current->next;
    }

    free(current->next);
    current->next = NULL;
    printf("Element deleted from the end.\n");
}

// Function to delete a node from a specified position in the linked list
void deleteAtPosition(struct Node** head, int position) {
    if (*head == NULL) {
        printf("List is empty. Nothing to delete.\n");
        return;
    }

    if (position < 1) {
        printf("Invalid position. Position should be >= 1.\n");
        return;
    }

    if (position == 1) {
        deleteFromBeginning(head);
        return;
    }

    struct Node* current = *head;
    struct Node* previous = NULL;
    for (int i = 1; i < position && current != NULL; ++i) {
        previous = current;
        current = current->next;
    }

    if (current == NULL) {
        printf("Position out of bounds.\n");
    } else {
        previous->next = current->next;
        free(current);
        printf("Element deleted from position %d.\n", position);
    }
}

// Function to search for a specific element in the linked list and display its position
int searchElement(struct Node* head, int key) {
    struct Node* current = head;
    int position = 1;

    while (current != NULL) {
        if (current->data == key) {
            return position;
        }
        current = current->next;
        position++;
    }

    return -1; // Element not found
}

// Function to calculate and display the length of the linked list
int calculateLength(struct Node* head) {
    struct Node* current = head;
    int length = 0;

    while (current != NULL) {
        length++;
        current = current->next;
    }

    return length;
}

// Function to reverse the linked list
void reverseList(struct Node** head) {
    struct Node* prev = NULL;
    struct Node* current = *head;
    struct Node* next = NULL;

    while (current != NULL) {
        next = current->next;
        current->next = prev;
        prev = current;
        current = next;
    }

    *head = prev;
}

// Function to sort the linked list using bubble sort
void sortList(struct Node** head) {
    int swapped, temp;
    struct Node* current;
    struct Node* last = NULL;

    if (*head == NULL) {
        printf("List is empty. Nothing to sort.\n");
        return;
    }

    do {
        swapped = 0;
        current = *head;

        while (current->next != last) {
            if (current->data > current->next->data) {
                temp = current->data;
                current->data = current->next->data;
                current->next->data = temp;
                swapped = 1;
            }
            current = current->next;
        }

        last = current;
    } while (swapped);
}

// Function to clear the input buffer
void clearInputBuffer() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}
