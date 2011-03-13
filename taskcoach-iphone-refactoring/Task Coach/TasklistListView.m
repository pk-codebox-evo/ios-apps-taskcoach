//
//  TasklistListView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TasklistView.h"
#import "TasklistListView.h"
#import "Task_CoachAppDelegate.h"
#import "CDList.h"
#import "CDFile.h"
#import "CDDomainObject.h"
#import "Configuration.h"
#import "i18n.h"

@implementation TasklistListView

@synthesize parent;

- (void)dealloc
{
    [resultsCtrl release];

    [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];

    NSFetchRequest *req = [[NSFetchRequest alloc] init];
    [req setEntity:[NSEntityDescription entityForName:@"CDList" inManagedObjectContext:getManagedObjectContext()]];
    NSSortDescriptor *sortdes = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES];
    [req setSortDescriptors:[NSArray arrayWithObject:sortdes]];
    [sortdes release];

    resultsCtrl = [[NSFetchedResultsController alloc] initWithFetchRequest:req managedObjectContext:getManagedObjectContext() sectionNameKeyPath:nil cacheName:nil];
    [req release];
    resultsCtrl.delegate = self;

    NSError *error;
    if (![resultsCtrl performFetch:&error])
    {
        UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:[NSString stringWithFormat:_("Could not fetch lists: %@"), [error localizedDescription]] delegate:nil cancelButtonTitle:_("OK") otherButtonTitles:nil];
        [alert show];
        [alert release];
    }
}

- (void)viewDidUnload
{
    [super viewDidUnload];

    [resultsCtrl release];
    resultsCtrl = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return NO;
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[resultsCtrl sections] count];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    id<NSFetchedResultsSectionInfo> infos = [[resultsCtrl sections] objectAtIndex:section];
    return [infos numberOfObjects];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
    {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:CellIdentifier] autorelease];
    }
    
    CDList *list = (CDList *)[resultsCtrl objectAtIndexPath:indexPath];
    cell.textLabel.text = list.name;

    if ([list isEqual:[Configuration instance].currentList])
    {
        cell.accessoryType = UITableViewCellAccessoryCheckmark;
        cell.editingAccessoryType = UITableViewCellAccessoryCheckmark;
    }
    else
    {
        cell.accessoryType = UITableViewCellAccessoryNone;
        cell.editingAccessoryType = UITableViewCellAccessoryNone;
    }

    if (list.file)
    {
        cell.detailTextLabel.text = [NSString stringWithFormat:_("File: %@"), list.file.name];
    }
    else
    {
        cell.detailTextLabel.text = @"";
    }

    return cell;
}

// Override to support editing the table view.
- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
    if (editingStyle == UITableViewCellEditingStyleDelete)
    {
        CDList *list = (CDList *)[resultsCtrl objectAtIndexPath:indexPath];
        NSLog(@"Delete objects belonging to list %@", list.name);

        NSFetchRequest *req = [[NSFetchRequest alloc] init];
        [req setEntity:[NSEntityDescription entityForName:@"CDDomainObject" inManagedObjectContext:getManagedObjectContext()]];
        [req setPredicate:[NSPredicate predicateWithFormat:@"list=%@", list]];
        NSError *error;
        NSArray *objects = [getManagedObjectContext() executeFetchRequest:req error:&error];
        [req release];
        
        if (objects)
        {
            for (CDDomainObject *obj in objects)
            {
                obj.file = nil;
                obj.list = nil;

                [getManagedObjectContext() deleteObject:obj];
            }
        }
        else
        {
            NSLog(@"Could not fetch objects: %@", [error localizedDescription]);
        }

        if (list.file)
        {
            [getManagedObjectContext() deleteObject:(NSManagedObject *)list.file];
            list.file = nil;
        }

        [getManagedObjectContext() deleteObject:list];

        if (![getManagedObjectContext() save:&error])
        {
            NSLog(@"Could not save: %@", [error localizedDescription]);
        }

        req = [[NSFetchRequest alloc] init];
        [req setEntity:[NSEntityDescription entityForName:@"CDList" inManagedObjectContext:getManagedObjectContext()]];
        NSArray *lists = [getManagedObjectContext() executeFetchRequest:req error:&error];
        [req release];

        if (lists)
        {
            if ([lists count] == 0)
            {
                [Configuration instance].currentList = nil;
                [[Configuration instance] save];
                [parent onSave:self];
            }
            else
            {
                [Configuration instance].currentList = [lists objectAtIndex:0];
                [[Configuration instance] save];
                [self.tableView reloadData];
            }
        }
        else
        {
            NSLog(@"Could not save: %@", [error localizedDescription]);
        }
    }   
}

/*
// Override to support rearranging the table view.
- (void)tableView:(UITableView *)tableView moveRowAtIndexPath:(NSIndexPath *)fromIndexPath toIndexPath:(NSIndexPath *)toIndexPath
{
}
*/

/*
// Override to support conditional rearranging of the table view.
- (BOOL)tableView:(UITableView *)tableView canMoveRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Return NO if you do not want the item to be re-orderable.
    return YES;
}
*/

#pragma mark - Table view delegate

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
    [self.tableView deselectRowAtIndexPath:indexPath animated:YES];

    CDList *list = [resultsCtrl objectAtIndexPath:indexPath];
    [Configuration instance].currentList = list;
    [[Configuration instance] save];
    [parent onSave:self];
}

#pragma mark - Fetched results controller delegate

- (void)controllerWillChangeContent:(NSFetchedResultsController *)controller
{
    [self.tableView beginUpdates];
}

- (void)controller:(NSFetchedResultsController *)controller didChangeSection:(id <NSFetchedResultsSectionInfo>)sectionInfo
           atIndex:(NSUInteger)sectionIndex forChangeType:(NSFetchedResultsChangeType)type
{
    switch(type) {
        case NSFetchedResultsChangeInsert:
            [self.tableView insertSections:[NSIndexSet indexSetWithIndex:sectionIndex]
                          withRowAnimation:UITableViewRowAnimationFade];
            break;
            
        case NSFetchedResultsChangeDelete:
            [self.tableView deleteSections:[NSIndexSet indexSetWithIndex:sectionIndex]
                          withRowAnimation:UITableViewRowAnimationFade];
            break;
    }
}

- (void)controller:(NSFetchedResultsController *)controller didChangeObject:(id)anObject
       atIndexPath:(NSIndexPath *)indexPath forChangeType:(NSFetchedResultsChangeType)type
      newIndexPath:(NSIndexPath *)newIndexPath
{
    UITableView *tableView = self.tableView;
    
    switch(type) {
            
        case NSFetchedResultsChangeInsert:
            [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath]
                             withRowAnimation:UITableViewRowAnimationFade];
            break;
            
        case NSFetchedResultsChangeDelete:
            [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath]
                             withRowAnimation:UITableViewRowAnimationFade];
            break;
            
        case NSFetchedResultsChangeUpdate:
            [tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationFade];
            break;
            
        case NSFetchedResultsChangeMove:
            [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath]
                             withRowAnimation:UITableViewRowAnimationFade];
            [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath]
                             withRowAnimation:UITableViewRowAnimationFade];
            break;
    }
}

- (void)controllerDidChangeContent:(NSFetchedResultsController *)controller
{
    [self.tableView endUpdates];
}

@end
